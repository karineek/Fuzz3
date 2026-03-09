# Fuzzing OLC (Java)

**1.** Get the code:
```
git clone https://github.com/google/open-location-code.git
cd open-location-code/
```

**2.** Install pre-requirements
```
sudo apt update
sudo apt install -y nodejs npm
node -v
```

  You should get something like this:
  ```
  v12.22.9
  8.5.1
  ```

**3.** Build and install it:
```
npm install
npm install open-location-code
```

**4.** Test it:
```
cat > test-pluscode.js <<'EOF'
const OpenLocationCode = require('open-location-code').OpenLocationCode;
const olc = new OpenLocationCode();

const full = olc.encode(51.5074, -0.1278);
console.log('Full:', full);

const short = olc.shorten(full, 51.5074, -0.1278);
console.log('Short:', short);

const recovered = olc.recoverNearest(short, 51.5074, -0.1278);
console.log('Recovered:', recovered);

const area = olc.decode(full);
console.log('Center:', area.latitudeCenter, area.longitudeCenter);
EOF

node test-pluscode.js
```

Output should indeed be two numbers:
```
user@node0:~/open-location-code$ node test-pluscode.js
Plus code: 9C3XGV4C+XV
Decoded center: 51.507437499999995 -0.12781249999999034
```
