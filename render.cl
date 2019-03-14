
//https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
//Naive implementation
float vsign(float3 p1, float3 p2, float3 p3)
{
    //TODO use vector and dot
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
}

bool PointInTriangle(float3 pt, float3 v1, float3 v2, float3 v3)
{
    float d1, d2, d3;
    bool has_neg, has_pos;

    d1 = vsign(pt, v1, v2);
    d2 = vsign(pt, v2, v3);
    d3 = vsign(pt, v3, v1);

    has_neg = (d1 < 0) || (d2 < 0) || (d3 < 0);
    has_pos = (d1 > 0) || (d2 > 0) || (d3 > 0);

    return !(has_neg && has_pos);
}



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
