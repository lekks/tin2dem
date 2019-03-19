
//https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
//Naive implementation

inline float vsign(float3 p1, float3 p2, float3 p3)
{
    float3 p13=p1-p3;
    float3 p23=p2-p3;
    return p13.x * p23.y - p23.x * p13.y; //cross product didn`t give speed (
}

bool PointInTriangle(float3 pt, float3 v1, float3 v2, float3 v3)
{
    float d1 = vsign(pt, v1, v2);
    float d2 = vsign(pt, v2, v3);
    float d3 = vsign(pt, v3, v1);

    bool has_neg = (d1 < 0) || (d2 < 0) || (d3 < 0);
    bool has_pos = (d1 > 0) || (d2 > 0) || (d3 > 0);

    return !(has_neg && has_pos);
}


// Shorter, but no speedup
/*
inline bool in_triangle(float3 pt, float3 v1, float3 v2, float3 v3)
{
    float3 pt1 = pt-v1;
    float d1 = cross(pt1, v1-v2).z;
    float d2 = cross(pt-v3, v2-v3).z;
    float d3 = cross(pt1, v3-v1).z;
    return !(((d1 < 0) || (d2 < 0) || (d3 < 0)) && ((d1 > 0) || (d2 > 0) || (d3 > 0)));
}
*/

__kernel void render(__const uint cols, __const __private float8 gt,
        __global const float3 * points, __global const float3 * z_coeffs,
        __global const int3 * faces, __const uint faces_cnt, __global char * filter,
        __global float * result, __global int * debug)
{
    int row = get_global_id(0);
    int col = get_global_id(1);
    int res_ndx = row * cols + col;
    float gx = col+0.5;
    float gy = row+0.5;
    float3 p;
    //TODO use dot
    p.x = gt.s0 + gx*gt.s1 + gy*gt.s2;
    p.y = gt.s3 + gx*gt.s4 + gy*gt.s5;
    p.z = 1;

    //printf("Geotransform = %2.2v8hlf\n", gt);
    //printf("x,y = (%.2f,%.2f)\n", x, y);

    for (int i=0; i < faces_cnt; ++i) {
        if(filter[i]) {
            int3 face = faces[i];
            if ( PointInTriangle (p, points[face.s0], points[face.s1], points[face.s2]) ) {
                float z = dot(p,z_coeffs[i]);
                if (z > result[res_ndx]) {
                    result[res_ndx]= z;
                }
                debug[res_ndx] = i+1;
            }
        }
    }
}

__kernel void filter(__const __private float4 bounds, __global const float3 * points,
        __global const int3 * faces, __const uint faces_cnt,
        __global char * result)
{
    int pos = get_global_id(0);
    int3 face = faces[pos];

    float3 p1=points[face.s0];
    float3 p2=points[face.s1];
    float3 p3=points[face.s2];

    float3 min_p = min(min(p1,p2), p3);
    float3 max_p = max(max(p1,p2), p3);

    if (max_p.x <= bounds.s0 || min_p.x >= bounds.s1 || max_p.y <= bounds.s2 || min_p.y >= bounds.s3) {
        result[pos] = false;
    } else {
        result[pos] = true;
    }


}
