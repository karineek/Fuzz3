#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$PROJECT_ROOT/build"
TMP_BUILD="$OUT_DIR/tmp_fastjson2_build"

if [ "${1:-}" == "--afl" ]; then
    echo "[!] Warning: --afl flag passed, but fastjson2 is a Java project. Building native Java wrapper instead."
fi

rm -rf "$TMP_BUILD" && mkdir -p "$TMP_BUILD" "$OUT_DIR"
cp -r "$PROJECT_ROOT/projects/fastjson2" "$TMP_BUILD/"

echo "[*] Building fastjson2 with Maven..."
cd "$TMP_BUILD/fastjson2"

# OSS-Fuzz Dockerfile specifies jdk 15 and skipping tests
mvn package -Dmaven.test.skip=true -Djdk.version=15 -q

# Find the generated jar (safer than relying on Maven evaluate plugin strings)
FASTJSON_JAR=$(ls "$PWD/core/target"/fastjson2-*.jar | grep -v "javadoc" | grep -v "sources" | head -n 1)

if [ ! -f "$FASTJSON_JAR" ]; then
    echo "ERROR: fastjson2 jar not found." >&2
    exit 1
fi

echo "[+] Built fastjson2 jar: $FASTJSON_JAR"

# Create a standalone Java wrapper (Removes the Jazzer dependency for blackbox CLI testing)
# This perfectly mimics the try/catch behavior of OSS-Fuzz's JsonFuzzer.java
cat << 'EOF' > "$TMP_BUILD/JsonWrapper.java"
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class JsonWrapper {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java JsonWrapper <file>");
            System.exit(1);
        }
        try {
            byte[] bytes = Files.readAllBytes(Paths.get(args[0]));
            String content = new String(bytes);
            JSON.parse(content);
        } catch (JSONException ignored) {
            // Expected parser exceptions, ignore just like JsonFuzzer.java
        } catch (Exception e) {
            // Unhandled exceptions (potential crashes)
            e.printStackTrace();
            System.exit(1);
        }
    }
}
EOF

echo "[*] Compiling Java wrapper..."
javac -cp "$FASTJSON_JAR" "$TMP_BUILD/JsonWrapper.java"

# Move artifacts to build directory
cp "$FASTJSON_JAR" "$OUT_DIR/fastjson2.jar"
cp "$TMP_BUILD/JsonWrapper.class" "$OUT_DIR/"

# Create the bash runner to act exactly like the C++ binaries
cat << EOF > "$OUT_DIR/fastjson2_fuzzer"
#!/usr/bin/env bash
java -cp "$OUT_DIR/fastjson2.jar:$OUT_DIR" JsonWrapper "\$1"
EOF
chmod +x "$OUT_DIR/fastjson2_fuzzer"

# Download the Google JSON dictionary as specified in the Dockerfile
echo "[*] Fetching JSON dictionary..."
wget -q "https://raw.githubusercontent.com/google/fuzzing/master/dictionaries/json.dict" -O "$OUT_DIR/fastjson2_fuzzer.dict" || true

echo "[+] fastjson2_fuzzer ready!"
