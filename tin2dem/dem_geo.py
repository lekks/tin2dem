import math


class DemInfo:
    def __init__(self, gt, width, height, offset_col=0, offset_row=0):
        self.gt = gt
        self.width = width
        self.height = height
        self.offset_col = offset_col
        self.offset_row = offset_row

    @staticmethod
    def from_envelope(west, east, south, north, pix_size, margins=None):
        if margins is None:
            margins = pix_size/2.0
        west -= margins
        east += margins
        south -= margins
        north += margins
        width = int(math.ceil((east - west)/pix_size))
        height = int(math.ceil((north - south)/pix_size))
        assert width > 0
        assert height > 0
        gt = [west, pix_size, 0, north, 0, -pix_size]
        return DemInfo(gt,width, height)

    def index_on_pos(self, x, y):
        '''
        Calculates pixel coordinates on (x,y) coordinates in dem projection
        :return: (row,col) index
        '''
        r = int((x - self.gt[0]) / self.gt[1])
        c = int((y - self.gt[3]) / self.gt[5])
        return r, c

    def pixel_coord(self, c, r):
        '''
        Calculates coordinates of pixel in dem projection system
        :return: (x,y)
        '''
        x = self.gt[0] + self.gt[1] * c
        y = self.gt[3] + self.gt[5] * r
        return x, y

    def bbox(self):
        bound_x, bound_y = self.pixel_coord(self.width, self.height)
        return self.gt[0], bound_x, bound_y, self.gt[3]


def split_dem(dem_info, width, height):
    for chunk_col in range(0, dem_info.width, width):
        chunk_width = min(width, dem_info.width - chunk_col)
        for chunk_row in range(0, dem_info.height, height):
            chunk_height = min(height, dem_info.height - chunk_row)
            xpos, ypos = dem_info.pixel_coord(chunk_col, chunk_row)
            gt = [xpos, dem_info.gt[1], dem_info.gt[2], ypos, dem_info.gt[4],  dem_info.gt[5]]
            dem_chunk = DemInfo(gt, chunk_width, chunk_height, chunk_col, chunk_row)
            yield dem_chunk
