; NIL LLVM AOT prototype: runtime context = fuel, depth, depth limit.
%nil.ctx = type { i64, i64, i64 }
declare void @nil_fail(i32, i64, i64) noreturn
declare { i64, i1 } @llvm.sadd.with.overflow.i64(i64, i64)
declare { i64, i1 } @llvm.ssub.with.overflow.i64(i64, i64)
declare { i64, i1 } @llvm.smul.with.overflow.i64(i64, i64)


declare void @nil_root_store(ptr, ptr)
declare ptr @nil_roots_enter(ptr, i64)
declare void @nil_roots_leave(ptr)
declare ptr @nil_format_f64(double, i64, i64)
declare ptr @nil_format_u64(i64, i64, i64)
declare ptr @nil_format_u128(ptr, i64, i64)
declare double @nil_parse_f64(ptr, i64, i64)
declare i64 @nil_parse_u64(ptr, i64, i64)
declare void @nil_parse_u128(ptr, ptr, i64, i64)
declare ptr @nil_sort(ptr, i64, i64, i64, i64)
declare ptr @nil_sort_unique(ptr, i64, i64, i64, i64)
declare ptr @nil_map(i64, i64)
declare void @nil_map_get_record(ptr, ptr, ptr, i64, i64, i64)
declare ptr @nil_map_update_record(ptr, ptr, ptr, i64, i1, i1, i64, i64)
declare i64 @nil_map_size(ptr, i64, i64)
declare i1 @nil_map_has(ptr, ptr, i64, i64)
declare ptr @nil_map_key(ptr, i64, i64, i64)
declare i64 @nil_map_get_int(ptr, ptr, i64, i64)
declare ptr @nil_map_get_bytes(ptr, ptr, i64, i64)
declare ptr @nil_map_insert_int(ptr, ptr, i64, i64, i64)
declare ptr @nil_map_insert_bytes(ptr, ptr, ptr, i64, i64)
declare ptr @nil_map_insert_unique_int(ptr, ptr, i64, i64, i64)
declare ptr @nil_map_insert_unique_bytes(ptr, ptr, ptr, i64, i64)
declare ptr @nil_map_put_int(ptr, ptr, i64, i64, i64)
declare ptr @nil_map_put_bytes(ptr, ptr, ptr, i64, i64)
declare ptr @nil_map_put_unique_int(ptr, ptr, i64, i64, i64)
declare ptr @nil_map_put_unique_bytes(ptr, ptr, ptr, i64, i64)
declare ptr @nil_literal(ptr, i64, i64, i64)
declare ptr @nil_make(i64, i64, i64, i64, i64)
declare i64 @nil_length(ptr)
declare i64 @nil_get(ptr, i64, i64, i64)
declare ptr @nil_set(ptr, i64, i64, i64, i64)
declare ptr @nil_set_unique(ptr, i64, i64, i64, i64)
declare ptr @nil_concat(ptr, ptr, i64, i64)
declare ptr @nil_concat_unique(ptr, ptr, i64, i64)
declare ptr @nil_slice(ptr, i64, i64, i64, i64)
declare ptr @nil_format(i64, i64, i64)
declare i64 @nil_parse(ptr, i64, i64)
declare ptr @nil_parsebuf(ptr, ptr, i64, i64)
declare i64 @nil_find(ptr, i64, i64, i64, i64)
declare ptr @nil_read(ptr, i64, i64)
declare i64 @nil_write(ptr, ptr, i64, i64)
declare i64 @nil_out(ptr, i64, i64)
!0 = !{!"branch_weights", i32 1, i32 1024}
; arithmetic: Wrapping; resource instrumentation: false
@nil_bytes_0_10 = private constant [1 x i8] [i8 10]
define i64 @nil_fn0(ptr %ctx, i64 %call_start, i64 %call_end, i64 %p0) {
b0:
  %nil_root_slots = alloca [5 x ptr], align 8
  store [5 x ptr] zeroinitializer, ptr %nil_root_slots, align 8
  %nil_root_frame = call ptr @nil_roots_enter(ptr %nil_root_slots, i64 5)
  %v1 = getelementptr [5 x ptr], ptr %nil_root_slots, i64 0, i64 0
  %v7 = getelementptr [5 x ptr], ptr %nil_root_slots, i64 0, i64 1
  %v9 = getelementptr [5 x ptr], ptr %nil_root_slots, i64 0, i64 2
  %v11 = getelementptr [5 x ptr], ptr %nil_root_slots, i64 0, i64 3
  %v23 = getelementptr [5 x ptr], ptr %nil_root_slots, i64 0, i64 4
  %v0 = call ptr @nil_make(i64 1, i64 0, i64 1, i64 6, i64 7)
  call void @nil_root_store(ptr %v1, ptr %v0)
  call void @nil_root_store(ptr %v1, ptr null)
  %v2 = call i64 @nil_length(ptr %v0)
  br label %b1
b1:
  %v3 = phi i64 [ 0, %b0 ], [ %v14, %b11 ]
  %v4 = phi ptr [ %v0, %b0 ], [ %v22, %b11 ]
  %v5 = phi i64 [ 0, %b0 ], [ %v24, %b11 ]
  %v6 = phi i64 [ %p0, %b0 ], [ %v6, %b11 ]
  call void @nil_root_store(ptr %v7, ptr %v4)
  %v8 = icmp slt i64 %v5, %v6
  br i1 %v8, label %b2, label %b3
b2:
  call void @nil_root_store(ptr %v7, ptr null)
  call void @nil_root_store(ptr %v9, ptr %v4)
  %v10 = call ptr @nil_literal(ptr @nil_bytes_0_10, i64 1, i64 38, i64 42)
  call void @nil_root_store(ptr %v11, ptr %v10)
  %v12 = call i1 @nil_plugin0_fn0(ptr %ctx, i64 29, i64 30, ptr %v4, ptr %v10)
  call void @nil_root_store(ptr %v11, ptr null)
  br i1 %v12, label %b4, label %b5
b3:
  call void @nil_root_store(ptr %v7, ptr null)
  call void @nil_roots_leave(ptr %nil_root_frame)
  ret i64 %v3
b4:
  br label %b6
b5:
  br label %b6
b6:
  %v13 = phi i64 [ 1, %b4 ], [ 0, %b5 ]
  %v14 = add i64 %v3, %v13
  %v15 = icmp eq i64 256, 0
  br i1 %v15, label %b7, label %b8
b7:
  call void @nil_fail(i32 3, i64 57, i64 58)
  unreachable
b8:
  %v16 = icmp eq i64 256, -1
  br i1 %v16, label %b9, label %b10, !prof !0
b9:
  %v17 = sub i64 0, %v5
  br label %b11
b10:
  %v18 = sdiv i64 %v5, 256
  br label %b11
b11:
  %v19 = phi i64 [ %v17, %b9 ], [ %v18, %b10 ]
  %v20 = mul i64 %v19, 256
  %v21 = sub i64 %v5, %v20
  %v22 = call ptr @nil_set_unique(ptr %v4, i64 0, i64 %v21, i64 50, i64 67)
  call void @nil_root_store(ptr %v23, ptr %v22)
  call void @nil_root_store(ptr %v9, ptr null)
  %v24 = add i64 %v5, 1
  call void @nil_root_store(ptr %v23, ptr null)
  br label %b1
}

define internal i1 @nil_plugin0_fn0(ptr %ctx, i64 %call_start, i64 %call_end, ptr %p0, ptr %p1) {
b0:
  %v0 = call i64 @nil_length(ptr %p0)
  %v1 = call i64 @nil_length(ptr %p1)
  %v2 = icmp eq i64 %v0, %v1
  br i1 %v2, label %b1, label %b2
b1:
  %v3 = call i64 @nil_length(ptr %p0)
  %v4 = call i64 @nil_length(ptr %p1)
  br label %b4
b2:
  br label %b3
b3:
  %v15 = phi i1 [ %v8, %b6 ], [ false, %b2 ]
  ret i1 %v15
b4:
  %v5 = phi ptr [ %p0, %b1 ], [ %v5, %b5 ]
  %v6 = phi ptr [ %p1, %b1 ], [ %v6, %b5 ]
  %v7 = phi i64 [ 0, %b1 ], [ %v14, %b5 ]
  %v8 = phi i1 [ true, %b1 ], [ %v13, %b5 ]
  %v9 = icmp slt i64 %v7, %v3
  br i1 %v9, label %b7, label %b8
b5:
  %v11 = call i64 @nil_get(ptr %v5, i64 %v7, i64 18446744073709551615, i64 18446744073709551615)
  %v12 = call i64 @nil_get(ptr %v6, i64 %v7, i64 18446744073709551615, i64 18446744073709551615)
  %v13 = icmp eq i64 %v11, %v12
  %v14 = add i64 %v7, 1
  br label %b4
b6:
  br label %b3
b7:
  br label %b9
b8:
  br label %b9
b9:
  %v10 = phi i1 [ %v8, %b7 ], [ false, %b8 ]
  br i1 %v10, label %b5, label %b6
}

