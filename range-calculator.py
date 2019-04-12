def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def in_range(num_,range_arr_):
    index = 0
    is_in_range = False
    for x in range_arr_:
        index += 1
        if x.start < num_ <= x.stop:
            is_in_range = True
            return index
    return index if is_in_range else 0

# def in_range(num_,range_arr_):
#     index = 0
#     is_in_range = False
#     for x in range_arr_:
#         if any(x.start < num_ <= x.stop for x in range_arr_):
#             is_in_range = True
#             return index
#     # for x in range_arr_:
#         # index += 1
#         # if (num_ - 1) in x:
#             # is_in_range = True
#             # return index
#     return index if is_in_range else 0


range_ = 20-5
range_arr_ = chunkIt(range(range_), 3)
print(range_arr_)
print(in_range(16,range_arr_))

