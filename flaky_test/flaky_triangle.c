/* WBL 5 Dec 2008 $Revision: 1.1 $ */

/*
Compile: gcc -o flaky_triangle flaky_triangle.c

Modifications:
WBL 30 Mar 2026 add noise via execution-time-of-c-program.c r1.1
*/
/*
STRUCTURED TESTING:
ANALYSIS AND EXTENSIONS
Arthur Henry Watson
Phd Thesis, Princeton
TR-528-96
November 1996
pages 149-150
ftp://ftp.cs.princeton.edu/techreports/1996/528.ps.gz

A.8 Code for \triangle" (\triangle()")
*/

/* classify triangles. The return codes are:
* 0 = not in order, 1 = right, 2 = obtuse, 3 = acute,
* 4 = isoceles, 5 = equilateral
*/
int
triangle(a, b, c)
int a, b, c;
{
int d;
L5:
if ((a >= b) & (b >= c))
goto L100;
return 0;
L100:
if (b == c)
goto L500;
a = a * a;
b = b * b;
c = c * c;
d = b + c;
if (a != d)
goto L200;
return 1;
L200:
if (a < d)
goto L300;
return 2;
L300:
return 3;
L500:
if ( (a == b) & (a == c) )
goto L600;
return 4;
L600:
return 5;
}

#include <stdlib.h>
/*execution-time-of-c-program.c r1.1*/
/*WBL 8 March 2026*/
/**/

//Modifications:
//WBL  8 Mar 2026 add gnu_get_libc_version

/*From https://stackoverflow.com/questions/5248915/execution-time-of-c-program?noredirect=1&lq=1 */

#include <time.h>
#include <stdio.h>
#include <gnu/libc-version.h>

int main(int argc, char *argv[])
{
    int a,b,c;
    clock_t tic = clock();

    a = atoi(argv[1]);
    b = atoi(argv[2]);
    c = atoi(argv[3]);

    const int tri = triangle(a, b, c);
    
    clock_t toc = clock();

    //printf("Elapsed: %f seconds ", (double)(toc - tic) / CLOCKS_PER_SEC);
    //printf("GLIBC version %s\n", gnu_get_libc_version());
    printf("%f\n", tri + (double)(toc - tic) / CLOCKS_PER_SEC);
    return 0;
}

