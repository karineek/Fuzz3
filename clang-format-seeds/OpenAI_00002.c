#if defined(AAA) && (BBB + 3) > 9 /* comment */ && !defined(CCC)
int f(void) { return 1; }
#elif defined(DDD) || defined(EEE)
int f(void) { return 2; } /* trailing */
#else
int f(void) { return 3; }
#endif
