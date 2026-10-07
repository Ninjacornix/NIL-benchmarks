/* Measurement-only; no arena/root/quota state is read or changed. */
#ifndef NIL_NATIVE_COPY_TRACE_PATH
#define NIL_NATIVE_COPY_TRACE_PATH ""
#endif
static uint64_t nil_measure_current_site, nil_measure_current_occurrence;
static uint64_t *nil_measure_occurrences;
static size_t nil_measure_capacity;
static FILE *nil_measure_output;
static void nil_measure_open(void) {
    if(!NIL_NATIVE_COPY_TRACE_PATH[0] || nil_measure_output)return;
    nil_measure_output=fopen(NIL_NATIVE_COPY_TRACE_PATH,"wb");if(!nil_measure_output)abort();
    fputs("site\toccurrence\trole\tbytes\tkind\n",nil_measure_output);
}
void nil_measure_site(uint64_t site) {
    nil_measure_open();
    if(site>=nil_measure_capacity) {
        size_t capacity=nil_measure_capacity?nil_measure_capacity:128;
        while(capacity<=site) {if(capacity>SIZE_MAX/2)abort();capacity*=2;}
        uint64_t *next=realloc(nil_measure_occurrences,capacity*sizeof(*next));if(!next)abort();
        memset(next+nil_measure_capacity,0,(capacity-nil_measure_capacity)*sizeof(*next));
        nil_measure_occurrences=next;nil_measure_capacity=capacity;
    }
    nil_measure_current_site=site;
    nil_measure_current_occurrence=++nil_measure_occurrences[site];
}
static void nil_measure_copy(unsigned role,uint64_t bytes,const char *kind) {
    if(!bytes || !NIL_NATIVE_COPY_TRACE_PATH[0])return;
    nil_measure_open();
    fprintf(nil_measure_output,"%" PRIu64 "\t%" PRIu64 "\t%u\t%" PRIu64 "\t%s\n",
        nil_measure_current_site,nil_measure_current_occurrence,role,bytes,kind);
}
__attribute__((destructor)) static void nil_measure_finish(void) {
    if(nil_measure_output && fclose(nil_measure_output))abort();
    free(nil_measure_occurrences);
}
