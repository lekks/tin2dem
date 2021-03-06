import logging
import os

import numpy as np
import pyopencl as cl
import pyopencl.cltypes

from tin2dem.plane_math import equation_plane, norm_z

log = logging.getLogger("render")


class Render:
    def __init__(self, surface, nodata_value=-1):

        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.filter_type = cl.cltypes.char

        self.nodata_value = nodata_value

        code = self.read_file("render.cl")
        self.prg = cl.Program(self.ctx, code)
        self.prg.build()
        points_vec = self.vertexes_as_ndarray(surface.vertices)
        self.points = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=points_vec)

        faces_vec = self.faces_as_ndarray(surface.faces)
        self.faces = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=faces_vec)
        self.faces_cnt = len(faces_vec)

        zcoef_vec = self.make_faces_zcoef(points_vec, faces_vec)
        self.zcoef_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=zcoef_vec)

        self.filter_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE,
                                    self.faces_cnt * np.dtype(self.filter_type).itemsize)

    def filter_bounds(self, dem_info):
        bounds = dem_info.bbox()
        bounds_vec = np.array(tuple(bounds), dtype=pyopencl.cltypes.float4)

        cl.enqueue_fill_buffer(self.queue, self.filter_buf, self.filter_type(0), 0,
                               self.faces_cnt * np.dtype(self.filter_type).itemsize)

        self.prg.filter(self.queue, (self.faces_cnt, 1), None,
                        bounds_vec, self.points,
                        self.faces, cl.cltypes.uint(self.faces_cnt),
                        self.filter_buf)

        return self.filter_buf

    def _select_filtered(self, filter_buf):
        filter_vec = np.empty(self.faces_cnt, dtype=self.filter_type)
        cl.enqueue_copy(self.queue, filter_vec, filter_buf)
        filtered = np.nonzero(filter_vec)[0].astype(pyopencl.cltypes.uint)
        return filtered

    def render_dem(self, dem_info, filter_buf=None):

        if filter_buf is None:
            filter_buf = self.filter_buf
            cl.enqueue_fill_buffer(self.queue, filter_buf, self.filter_type(1), 0,
                                   self.faces_cnt * np.dtype(self.filter_type).itemsize)

        filtered_vec = self._select_filtered(filter_buf)
        filtered_count = len(filtered_vec)
        log.debug("Filtered {} triangles".format(filtered_count))

        shape = (dem_info.height, dem_info.width)

        debug_vec = np.empty(shape, dtype=cl.cltypes.int)
        debug_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, debug_vec.nbytes)
        cl.enqueue_fill_buffer(self.queue, debug_buf, cl.cltypes.int(-1), 0, debug_vec.nbytes)

        result_vec = np.empty(shape, dtype=cl.cltypes.float)
        result_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, result_vec.nbytes)
        cl.enqueue_fill_buffer(self.queue, result_buf, cl.cltypes.float(self.nodata_value), 0, result_vec.nbytes)

        if filtered_count > 0:
            filtered_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY, filtered_vec.nbytes)
            cl.enqueue_copy(self.queue, filtered_buf, filtered_vec)
            gt = np.array(tuple(dem_info.gt + [0, 0]), dtype=pyopencl.cltypes.float8)

            self.prg.render(self.queue, shape, None,
                            np.uint32(shape[1]), gt,
                            self.points, self.zcoef_buf,
                            self.faces,
                            filtered_buf, cl.cltypes.uint(filtered_count),
                            result_buf, debug_buf)

        cl.enqueue_copy(self.queue, result_vec, result_buf)
        cl.enqueue_copy(self.queue, debug_vec, debug_buf)

        return result_vec, debug_vec

    @staticmethod
    def vertexes_as_ndarray(vertices):
        vertices.sort(key=lambda x: x[0])
        max_id = vertices[-1][0]
        log.info("Max vertex id is {}".format(max_id))
        arr_vert = np.zeros((max_id + 1,), cl.cltypes.float3)
        for i, x, y, z in vertices:
            arr_vert[i] = x, y, z, 0
        return arr_vert

    @staticmethod
    def faces_as_ndarray(faces):
        arr_faces = np.zeros((len(faces),), cl.cltypes.int3)
        for i, (a, b, c) in enumerate(faces):
            arr_faces[i] = (a, b, c, 0)
        return arr_faces

    @staticmethod
    def make_faces_zcoef(points, faces):
        log.info("Calculating z coefficients")
        arr_coefs = np.zeros((len(faces),), cl.cltypes.float4)

        orth_cnt = 0
        for i, pnts in enumerate(faces):
            p1 = tuple(points[pnts[0]])[:3]
            p2 = tuple(points[pnts[1]])[:3]
            p3 = tuple(points[pnts[2]])[:3]
            eq_coef = equation_plane(p1, p2, p3)
            if eq_coef[2] == 0:
                log.debug("Orthogonal face {}, points {} at {}".format(i, tuple(pnts)[:3], (p1, p2, p3), eq_coef))
                orth_cnt += 1
            else:
                za, zb, zc = norm_z(eq_coef)
                arr_coefs[i] = (za, zb, zc, 1)
        log.info("Found {} orthogonal faces".format(orth_cnt))
        return arr_coefs

    @staticmethod
    def read_file(rel_path):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, 'r') as f:
            return f.read()
