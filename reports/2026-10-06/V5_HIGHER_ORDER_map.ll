; NIL LLVM AOT prototype: runtime context = fuel, depth, depth limit.
%nil.ctx = type { i64, i64, i64 }
declare void @nil_fail(i32, i64, i64) noreturn
declare { i64, i1 } @llvm.sadd.with.overflow.i64(i64, i64)
declare { i64, i1 } @llvm.ssub.with.overflow.i64(i64, i64)
declare { i64, i1 } @llvm.smul.with.overflow.i64(i64, i64)


declare ptr @nil_record_make(i64, ptr, ptr, i64, i64)
declare void @nil_record_get(ptr, i64, ptr, i64, i64)
declare ptr @nil_record_set(ptr, i64, ptr, i1, i64, i64)
declare ptr @nil_record_concat(ptr, ptr, i1, i64, i64)
declare ptr @nil_record_slice(ptr, i64, i64, i64, i64)
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
declare i1 @nil_bulk_compare(ptr, ptr)
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
declare ptr @nil_env(ptr, i64, i64)
declare i64 @nil_random(i64, i64)
declare ptr @nil_directory(ptr, i64, i64)
declare ptr @nil_read(ptr, i64, i64)
declare i64 @nil_write(ptr, ptr, i64, i64)
declare i64 @nil_out(ptr, i64, i64)
!0 = !{!"branch_weights", i32 1, i32 1024}
; arithmetic: Wrapping; resource instrumentation: false
define internal i64 @nil_fn0(ptr %ctx, i64 %call_start, i64 %call_end, ptr %p0) alwaysinline {
b0:
  %nil_root_slots = alloca [2 x ptr], align 8
  store [2 x ptr] zeroinitializer, ptr %nil_root_slots, align 8
  %nil_root_frame = call ptr @nil_roots_enter(ptr %nil_root_slots, i64 2)
  %v0 = getelementptr [2 x ptr], ptr %nil_root_slots, i64 0, i64 0
  %v2 = getelementptr [2 x ptr], ptr %nil_root_slots, i64 0, i64 1
  call void @nil_root_store(ptr %v0, ptr %p0)
  %v1 = call ptr @nil_read(ptr %p0, i64 9, i64 10)
  call void @nil_root_store(ptr %v2, ptr %v1)
  call void @nil_root_store(ptr %v0, ptr null)
  call void @nil_root_store(ptr %v2, ptr null)
  %v3 = call i64 @nil_fn2(ptr %ctx, i64 4, i64 18, ptr %v1)
  call void @nil_roots_leave(ptr %nil_root_frame)
  ret i64 %v3
}

define i64 @nil_fn1(ptr %ctx, i64 %call_start, i64 %call_end, i64 %p0) {
b0:
  %v0 = icmp eq i64 %p0, 10
  br i1 %v0, label %b1, label %b2
b1:
  br label %b3
b2:
  br label %b3
b3:
  %v1 = phi i64 [ 1, %b1 ], [ 0, %b2 ]
  ret i64 %v1
}

define internal i64 @nil_fn2(ptr %ctx, i64 %call_start, i64 %call_end, ptr %p0) alwaysinline {
b0:
  %v0 = getelementptr i8, ptr %p0, i64 40
  %v1 = call i64 @nil_length(ptr %p0)
  br label %b1
b1:
  %v2 = phi ptr [ %p0, %b0 ], [ %v2, %b2 ]
  %v3 = phi i64 [ 0, %b0 ], [ %v6, %b2 ]
  %v4 = phi i64 [ 0, %b0 ], [ %v11, %b2 ]
  %v5 = icmp slt i64 %v3, %v1
  br i1 %v5, label %b2, label %b3
b2:
  %v6 = add i64 %v3, 1
  %v7 = getelementptr i8, ptr %v0, i64 %v3
  %v8 = load i8, ptr %v7, align 1
  %v9 = zext i8 %v8 to i64
  %v10 = call i64 @nil_fn1(ptr %ctx, i64 50, i64 58, i64 %v9)
  %v11 = add i64 %v4, %v10
  br label %b1
b3:
  ret i64 %v4
}

define void @nil_entry(ptr %ctx, ptr %args, ptr %out) {
b0:
  %v0 = getelementptr i64, ptr %args, i64 0
  %v1 = load i64, ptr %v0, align 8
  %v2 = inttoptr i64 %v1 to ptr
  %v3 = call i64 @nil_fn0(ptr %ctx, i64 18446744073709551615, i64 18446744073709551615, ptr %v2)
  %v4 = getelementptr i64, ptr %out, i64 0
  store i64 %v3, ptr %v4, align 8
  ret void
}
