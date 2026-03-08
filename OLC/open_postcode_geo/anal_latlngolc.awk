#WBL 8 March 2026 analyse results of run_latlngolc.bat r1.3

#Usage
#gawk -f anal_latlngolc.awk latlngolc.bat latlngolc.out

BEGIN{
  rev = "$Revision: 1.1 $";
  rev = substr(rev,2,length(rev)-3);
  print "#anal_latlngolc.awk",rev,strftime();
}
BEGINFILE{print "#reading",FILENAME}
(index($0,"#")==1){print;next}
($1=="latlngolc" && $4==">>"){I1++; input[I1]  = $2" "$3;}
(index(FILENAME,".out"))     {I2++; output[I2] = $0}
END{
  print I1,I2;
  if(I1!=I2) error10();
  I=I1;
  if(I!=2589831) error11();
#check deterministic
  for(i=1;i<=I;i++) {
    u = input[i];
    iused[u] = sprintf("%s %s",iused[u], i);
    v = output[i];
    oused[v] = sprintf("%s %s",oused[v], i);
  }
  for(i in iused){
    u = iused[i];
    n = split(u,tn);
    ll = tn[1];
    if(!(ll in output)) {print "i=\""i"\" u=\""u"\"","ll="ll; error20()}
    v = output[ll];
    if(!(v in oused)) {print "i=\""i"\" u=\""u"\"","ll="ll,"v=\""v"\""; error21()}
    x = oused[v];
    if(verbose)print "i=\""i"\"","u=\""u"\"","v=\""v"\"","x=\""x"\"";
    m = split(x,tm);
    if(u != x) error22();
    if(n != m) error30();
    for(j=1;j<=n;j++){if(tn[j] != tm[j]) error31();}
    for(j=2;j<=n;j++){
      if(i!=input[tn[j]]){print "i=\""i"\" u=\""u"\"","n="n,"j="j; error32();}
    }
    #have already checked latlngolc (for open_postcode_geo.dat) is deterministic
    #Nevertheless calculate entropy anyway
    dist[++Ih] = n/I;
  }
  if(Ih<10 || Ih > I) error40();
  printf("Entropy (bits) of inputs and outputs %s %s ",Ih,FILENAME);
  H(Ih,dist);
}
    
#From ~/gp/info_lgp/entropy.awk r1.2a

function log2(x){ return log(x)/log(2)}
function h(x){ return -x*log2(x)}
function H(n,x,   i,sum){
  for(i=1;i<=n;i++) { #printf("%s ",h(x[i]));
      sum+=h(x[i])}
  printf("%s\n",sum);
}
