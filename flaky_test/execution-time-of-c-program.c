/*WBL 8 March 2026*/
/*Compile: gcc -o time_me execution-time-of-c-program.c */

//Modifications:
//WBL  8 Mar 2026 add gnu_get_libc_version

/*From https://stackoverflow.com/questions/5248915/execution-time-of-c-program?noredirect=1&lq=1 */

#include <time.h>
#include <stdio.h>
#include <gnu/libc-version.h>

int main()
{
    clock_t tic = clock();

    //my_expensive_function_which_can_spawn_threads();
    
    clock_t toc = clock();

    printf("Elapsed: %f seconds ", (double)(toc - tic) / CLOCKS_PER_SEC);
    printf("GLIBC version %s\n", gnu_get_libc_version());

    return 0;
}
