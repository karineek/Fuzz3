#WBL 6 May 2020  $Revision: 1.2a $

#Modification:
#WBL 25 Jan 2026 remove stderr output
#WBL 26 Jun 2025 Add print distribution as sanity check for rounding error
#WBL 20 May 2022 based on H.awk r1.2

BEGIN{ 
  if(ncol1=="") {print "bad ncol1"; exit}
}
(NF>=ncol1) {
  data[$ncol1]++;
  total++;
}

END{
  i=0;
# print "ncol1="ncol1,"total="total > "/dev/stderr";
  for (j in data) x[++i] = data[j]/total;
  H(i,x);

  #calculate distribution histogram (as sanity check)
  n = asort(data);
  for(j=1;j<=n;j++) {k=data[j];if(k>max) max=k; c[k]++;}
  for(j=1;j<=max;j++) print j,c[j];
}


function log2(x){ return log(x)/log(2)}
function h(x){ return -x*log2(x)}
function H(n,x,   i,sum){
  for(i=1;i<=n;i++) { #printf("%s ",h(x[i]));
      sum+=h(x[i])}
  printf("%s\n",sum);
}
