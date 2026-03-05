#define X_FIELDS(X) \
  X(id,   int)      \
  X(name, char *)   \
  X(flag, unsigned)

struct S {
#define X(n, t) t n;
  X_FIELDS(X)
#undef X
};
