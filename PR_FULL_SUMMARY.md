# PR Full Summary: normalize/no-paren-sweep

This PR normalizes Gulf of Mexico .gom files to use the canonical no-paren calling style (e.g., fn(a, b)! -> fn a, b!) across examples and programs, fixes interpolation and parenthesis issues, and also adds Qt IDE improvements (Open Web IDE menu + sanitized console error styling).

## Files modified (branch vs main)
- PR_SUMMARY.md
- compiler/examples/comprehensive_test.gom
- compiler/examples/test_maps.gom
- examples/mandelbrot.gom
- gulfofmexico/ide/app.py
- programs/01_basics/03_arrays.gom
- programs/01_basics/04_probabilistic.gom
- programs/01_basics/06_classes.gom
- programs/02_features/12_async.gom
- programs/02_features/14_arithmetic.gom
- programs/03_graphics/18_generative_art.gom
- programs/03_graphics/19_mandelbrot.gom
- programs/03_graphics/mandelbrot_simple.gom
- programs/04_satirical/19_passive_aggressive_errors.gom
- programs/04_satirical/21_corporate_speak.gom
- programs/04_satirical/22_satirical_showcase.gom
- programs/04_satirical/24_superstitious_programming.gom
- programs/04_satirical/25_ultimate_satire.gom
- programs/04_satirical/26_quantum_programming.gom
- programs/04_satirical/27_time_travel.gom
- programs/04_satirical/28_quantum_time_spectacular.gom
- programs/05_analysis/36_base_numbers.gom
- programs/05_analysis/37_base_simple.gom
- programs/05_analysis/38_base_practical.gom
- programs/05_analysis/39_statistics.gom
- programs/05_analysis/40_financial.gom
- programs/05_analysis/41_business.gom
- programs/05_analysis/42_scientific.gom
- programs/demos/async_pipeline.gom
- programs/demos/banking_system.gom
- programs/demos/calculator.gom
- programs/demos/feature_showcase.gom
- programs/demos/grand_deluxe_demo.gom
- programs/demos/multi_file.gom
- programs/demos/rpg_character.gom
- programs/demos/task_manager.gom
- programs/examples/00_complete_showcase.gom
- tests/test_ide_app.py


--- Full unified diff (main...HEAD) ---
diff --git a/PR_SUMMARY.md b/PR_SUMMARY.md
new file mode 100644
index 0000000..c72298b
--- /dev/null
+++ b/PR_SUMMARY.md
@@ -0,0 +1,1662 @@
+# PR: Normalize .gom Calls — no-paren canonicalization
+
+This branch normalizes Gulf of Mexico (GOM) example/program files to the canonical no-paren call style (e.g. fn(a, b)! -> fn a, b!). Includes interpolation & string fixes where needed.
+
+## Files changed (HEAD)
+"
+"
+compiler/examples/comprehensive_test.gom
+compiler/examples/test_maps.gom
+examples/mandelbrot.gom
+programs/01_basics/03_arrays.gom
+programs/01_basics/04_probabilistic.gom
+programs/01_basics/06_classes.gom
+programs/02_features/12_async.gom
+programs/02_features/14_arithmetic.gom
+programs/03_graphics/18_generative_art.gom
+programs/03_graphics/19_mandelbrot.gom
+programs/03_graphics/mandelbrot_simple.gom
+programs/04_satirical/19_passive_aggressive_errors.gom
+programs/04_satirical/21_corporate_speak.gom
+programs/04_satirical/22_satirical_showcase.gom
+programs/04_satirical/24_superstitious_programming.gom
+programs/04_satirical/25_ultimate_satire.gom
+programs/04_satirical/26_quantum_programming.gom
+programs/04_satirical/27_time_travel.gom
+programs/04_satirical/28_quantum_time_spectacular.gom
+programs/05_analysis/36_base_numbers.gom
+programs/05_analysis/37_base_simple.gom
+programs/05_analysis/38_base_practical.gom
+programs/05_analysis/39_statistics.gom
+programs/05_analysis/40_financial.gom
+programs/05_analysis/41_business.gom
+programs/05_analysis/42_scientific.gom
+programs/demos/async_pipeline.gom
+programs/demos/banking_system.gom
+programs/demos/calculator.gom
+programs/demos/feature_showcase.gom
+programs/demos/grand_deluxe_demo.gom
+programs/demos/multi_file.gom
+programs/demos/rpg_character.gom
+programs/demos/task_manager.gom
+programs/examples/00_complete_showcase.gom
+
+--- Diff (HEAD) ---
+commit 4580f6538897ff9a45787766c2895cc67dd6a6fd
+Author: James-HoneyBadger <james@honey-badger.org>
+Date:   Wed Dec 3 09:10:23 2025 -0600
+
+    Normalize .gom calls to canonical no-paren style; fix interpolation/paren mismatches
+
+diff --git a/compiler/examples/comprehensive_test.gom b/compiler/examples/comprehensive_test.gom
+index 4cfda50..b905f7b 100644
+--- a/compiler/examples/comprehensive_test.gom
++++ b/compiler/examples/comprehensive_test.gom
+@@ -5,7 +5,7 @@ print "=== GULF OF MEXICO COMPILER - COMPREHENSIVE TEST ==="!
+
+ // Test 1: Map Support
+ print "\n1. Map/Dictionary Support"!
+-const config = Map()!
++const config = Map !
+ print "  Created empty map: OK"!
+
+ // Test 2: Arrays with -1 indexing
+diff --git a/compiler/examples/test_maps.gom b/compiler/examples/test_maps.gom
+index 2ec0cbc..ffc3599 100644
+--- a/compiler/examples/test_maps.gom
++++ b/compiler/examples/test_maps.gom
+@@ -2,7 +2,7 @@
+
+ print "=== Testing Map/Dictionary Support ==="!
+
+-const person = Map()!
++const person = Map !
+ print "Created empty Map"!
+
+ print "\n=== Testing Array Operations ==="!
+diff --git a/examples/mandelbrot.gom b/examples/mandelbrot.gom
+index 4c0078d..2fdfe50 100644
+--- a/examples/mandelbrot.gom
++++ b/examples/mandelbrot.gom
+@@ -9,42 +9,42 @@ const canvas = Canvas 600, 400, "white"!
+ print "Canvas initialized - drawing fractal pattern..."!
+
+ // Create color palette from dark blue to white
+-const c0 = Color(0, 0, 51)!      // Darkest blue
+-const c1 = Color(0, 0, 102)!     // Dark blue
+-const c2 = Color(0, 0, 153)!     // Medium dark blue
+-const c3 = Color(0, 0, 204)!     // Medium blue
+-const c4 = Color(0, 0, 255)!     // Bright blue
+-const c5 = Color(51, 51, 255)!   // Purple-blue
+-const c6 = Color(102, 102, 255)! // Light purple
+-const c7 = Color(153, 153, 255)! // Very light purple
+-const c8 = Color(204, 204, 255)! // Almost white
+-const c9 = Color(255, 255, 255)! // White
++const c0 = Color 0, 0, 51!      // Darkest blue
++const c1 = Color 0, 0, 102!     // Dark blue
++const c2 = Color 0, 0, 153!     // Medium dark blue
++const c3 = Color 0, 0, 204!     // Medium blue
++const c4 = Color 0, 0, 255!     // Bright blue
++const c5 = Color 51, 51, 255!   // Purple-blue
++const c6 = Color 102, 102, 255! // Light purple
++const c7 = Color 153, 153, 255! // Very light purple
++const c8 = Color 204, 204, 255! // Almost white
++const c9 = Color 255, 255, 255! // White
+
+ print "Drawing gradient background..."!
+
+ // Draw horizontal gradient bands (10 bands of 40 pixels each)
+-canvas.pixel(-1, 0, c0)!
+-canvas.pixel(-1, 40, c1)!
+-canvas.pixel(-1, 80, c2)!
+-canvas.pixel(-1, 120, c3)!
+-canvas.pixel(-1, 160, c4)!
+-canvas.pixel(-1, 200, c5)!
+-canvas.pixel(-1, 240, c6)!
+-canvas.pixel(-1, 280, c7)!
+-canvas.pixel(-1, 320, c8)!
+-canvas.pixel(-1, 360, c9)!
++canvas.pixel -1, 0, c0!
++canvas.pixel -1, 40, c1!
++canvas.pixel -1, 80, c2!
++canvas.pixel -1, 120, c3!
++canvas.pixel -1, 160, c4!
++canvas.pixel -1, 200, c5!
++canvas.pixel -1, 240, c6!
++canvas.pixel -1, 280, c7!
++canvas.pixel -1, 320, c8!
++canvas.pixel -1, 360, c9!
+
+ print "Drawing central fractal bulb..."!
+
+ // Draw some pixels to create a simple pattern
+-canvas.pixel(299, 199, c9)!
+-canvas.pixel(300, 200, c8)!
+-canvas.pixel(298, 198, c7)!
++canvas.pixel 299, 199, c9!
++canvas.pixel 300, 200, c8!
++canvas.pixel 298, 198, c7!
+
+ print "Finalizing fractal image..."!
+
+ // Save the fractal image
+-canvas.save("mandelbrot.png")!
++canvas.save "mandelbrot.png"!
+
+ print ""!
+ print "===================================="!
+diff --git a/programs/01_basics/03_arrays.gom b/programs/01_basics/03_arrays.gom
+index 581c602..fe99798 100644
+--- a/programs/01_basics/03_arrays.gom
++++ b/programs/01_basics/03_arrays.gom
+@@ -2,10 +2,10 @@
+
+ const numbers = [10, 20, 30, 40, 50]!
+
+-print "First element (index -1: ${numbers[-1]}")!
+-print "Second element (index 0: ${numbers[0]}")!
+-print "Third element (index 1: ${numbers[1]}")!
+-print "Last element (index 3: ${numbers[3]}")!
++print "First element (index -1): ${numbers[-1]}"!
++print "Second element (index 0): ${numbers[0]}"!
++print "Third element (index 1): ${numbers[1]}"!
++print "Last element (index 3): ${numbers[3]}"!
+
+ // Fractional indexing
+ const colors = ["red", "blue"]!
+diff --git a/programs/01_basics/04_probabilistic.gom b/programs/01_basics/04_probabilistic.gom
+index e348c48..449772a 100644
+--- a/programs/01_basics/04_probabilistic.gom
++++ b/programs/01_basics/04_probabilistic.gom
+@@ -7,7 +7,7 @@ var value = 20!!
+ print "Value with confidence 2: ${value}"!
+
+ var value = 5!!!
+-print "Value with confidence 3 (wins!: ${value}")!
++print "Value with confidence 3 (wins!): ${value}"!
+
+ var value = 100!!!!
+-print "Value with confidence 4 (highest!: ${value}")!
++print "Value with confidence 4 (highest!): ${value}"!
+diff --git a/programs/01_basics/06_classes.gom b/programs/01_basics/06_classes.gom
+index f6d3336..b3dba8e 100644
+--- a/programs/01_basics/06_classes.gom
++++ b/programs/01_basics/06_classes.gom
+@@ -18,10 +18,10 @@ class Person {
+ const alice = new Person!
+ alice.name = "Alice"!
+ alice.age = 25!
+-alice.introduce()!
++alice.introduce !
+
+ const bob = new Person!
+ bob.name = "Bob"!
+ bob.age = 30!
+-bob.introduce()!
+-bob.birthday()!
++bob.introduce !
++bob.birthday !
+diff --git a/programs/02_features/12_async.gom b/programs/02_features/12_async.gom
+index 4b1c0bb..d854c5e 100644
+--- a/programs/02_features/12_async.gom
++++ b/programs/02_features/12_async.gom
+@@ -11,8 +11,8 @@ async function processData(value) => {
+ }!
+
+ // Call async functions
+-const result = await fetchData()!
++const result = await fetchData!
+ print "Fetched result: ${result}"!
+
+-const processed = await processData(result)!
++const processed = await processData result!
+ print "Processed result: ${processed}"!
+diff --git a/programs/02_features/14_arithmetic.gom b/programs/02_features/14_arithmetic.gom
+index 8c937f3..507738e 100644
+--- a/programs/02_features/14_arithmetic.gom
++++ b/programs/02_features/14_arithmetic.gom
+@@ -11,4 +11,4 @@ print "Power: ${a} ^ ${b} = ${a ^ b}"!
+
+ // Complex expressions
+ const result = (a + b) * 2 ^ 3!
+-print "(${a} + ${b} * 2 ^ 3 = ${result}")!
++print "(${a} + ${b} * 2 ^ 3 = ${result})"!
+diff --git a/programs/03_graphics/18_generative_art.gom b/programs/03_graphics/18_generative_art.gom
+index 110a71f..d7fe2bf 100644
+--- a/programs/03_graphics/18_generative_art.gom
++++ b/programs/03_graphics/18_generative_art.gom
+@@ -17,7 +17,7 @@ function fn drawCircleGrid() {
+       var otherColor "blue"!!!
+
+       // Use maybe to randomly choose properties
+-      const useOther = Boolean(maybe)!
++      const useOther = Boolean maybe!
+       const finalColor = useOther ? otherColor : circleColor!
+
+       // Position with -1 based indexing
+@@ -27,29 +27,29 @@ function fn drawCircleGrid() {
+       // Radius with some randomness
+       var baseRadius 15!!
+       var bigRadius 20!!!
+-      const radius = Boolean(maybe) ? bigRadius : baseRadius!
++      const radius = Boolean maybe ? bigRadius : baseRadius!
+
+-      canvas.circle(x, y, radius, finalColor)!
++      canvas.circle x, y, radius, finalColor!
+
+       var col col + 1!
+    }
+
+    // Draw 15 circles in this row
+    drawRow!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
+-   drawRow()!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
++   drawRow!
+
+    var row row + 1!
+ }
+diff --git a/programs/03_graphics/19_mandelbrot.gom b/programs/03_graphics/19_mandelbrot.gom
+index a742d6d..88a10ad 100644
+--- a/programs/03_graphics/19_mandelbrot.gom
++++ b/programs/03_graphics/19_mandelbrot.gom
+@@ -3,7 +3,7 @@ print "Starting Mandelbrot generation..."!
+
+ const width = 100!
+ const height = 100!
+-const canvas = Canvas(width, height, "black")!
++const canvas = Canvas width, height, "black"!
+
+ print "Canvas created"!
+
+@@ -23,7 +23,7 @@ var col = -1!
+ // Draw a simple gradient as a test
+ function drawPixel(x, y, iter) => {
+    const color = iter == 0 ? c0 : (iter == 1 ? c1 : (iter == 2 ? c2 : c3))!
+-   canvas.pixel(x, y, color)!
++   canvas.pixel x, y, color!
+ }!
+
+ // Process one pixel
+@@ -35,7 +35,7 @@ function processPixel() => {
+    // Simple iteration count (just based on position for now)
+    const iter = ((col + row) % 4)!
+
+-   drawPixel(col, row, iter)!
++   drawPixel col, row, iter!
+
+    col = col + 1!
+ }!
+@@ -44,35 +44,35 @@ function processPixel() => {
+ function processRow() => {
+    col = -1!
+
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
+-   processPixel()!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
++   processPixel!
+
+    row = row + 1!
+ }!
+
+ print "Starting to draw..."!
+
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
+-processRow()!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
++processRow!
+
+ print "Drawing complete!"!
+
+-canvas.save("mandelbrot.png")!
++canvas.save "mandelbrot.png"!
+
+ print "Mandelbrot set saved to mandelbrot.png"!
+diff --git a/programs/03_graphics/mandelbrot_simple.gom b/programs/03_graphics/mandelbrot_simple.gom
+index d6d6d51..9d9586d 100644
+--- a/programs/03_graphics/mandelbrot_simple.gom
++++ b/programs/03_graphics/mandelbrot_simple.gom
+@@ -3,15 +3,15 @@
+
+ print "Creating fractal art..."!
+
+-const canvas = Canvas(400, 300, "black")!
++const canvas = Canvas 400, 300, "black"!
+
+ // Color palette - blues to whites
+-const c0 = Color(0, 0, 51)!     // Dark blue
+-const c1 = Color(0, 0, 102)!    // Medium blue
+-const c2 = Color(51, 102, 204)! // Bright blue
+-const c3 = Color(102, 153, 255)! // Light blue
+-const c4 = Color(204, 229, 255)! // Very light blue
+-const c5 = Color(255, 255, 255)! // White
++const c0 = Color 0, 0, 51!     // Dark blue
++const c1 = Color 0, 0, 102!    // Medium blue
++const c2 = Color 51, 102, 204! // Bright blue
++const c3 = Color 102, 153, 255! // Light blue
++const c4 = Color 204, 229, 255! // Very light blue
++const c5 = Color 255, 255, 255! // White
+
+ print "Colors created"!
+
+diff --git a/programs/04_satirical/19_passive_aggressive_errors.gom b/programs/04_satirical/19_passive_aggressive_errors.gom
+index 6972155..c005fda 100644
+--- a/programs/04_satirical/19_passive_aggressive_errors.gom
++++ b/programs/04_satirical/19_passive_aggressive_errors.gom
+@@ -5,7 +5,7 @@ print "=== Passive-Aggressive Error Handling ==="!
+
+ // Example 1: Division by zero (whatever!)
+ try {
+-   const result = Number(10) / Number(0)!
++   const result = Number(10) / Number 0!
+    print "Result:", result!
+ } whatever {
+    print "Math is hard, let's go shopping"!
+@@ -20,7 +20,7 @@ try {
+
+ // Example 3: Invalid operation (whatever!)
+ try {
+-   const broken = String("hello") - Number(5)!
++   const broken = String("hello") - Number 5!
+    print broken!
+ } whatever {
+    print "Whatever, I didn't want to do that anyway"!
+@@ -28,7 +28,7 @@ try {
+
+ // Example 4: Actually successful code
+ try {
+-   const x = Number(42)!
++   const x = Number 42!
+    print "Success! x =", x!
+ } whatever {
+    print "This shouldn't print"!
+diff --git a/programs/04_satirical/21_corporate_speak.gom b/programs/04_satirical/21_corporate_speak.gom
+index 7e1888d..cbd4d63 100644
+--- a/programs/04_satirical/21_corporate_speak.gom
++++ b/programs/04_satirical/21_corporate_speak.gom
+@@ -5,37 +5,37 @@ print "=== Corporate Synergy Meeting ==="!
+
+ // synergize: Combine two values
+ print "\n1. SYNERGIZE (combining values):"!
+-const name1 = String("Innovative")!
+-const name2 = String("Solutions")!
++const name1 = String "Innovative"!
++const name2 = String "Solutions"!
+ synergize name1, name2!
+ print "  Company name:", name1, "+", name2!
+
+-const revenue = Number(100000)!
+-const profit = Number(50000)!
++const revenue = Number 100000!
++const profit = Number 50000!
+ synergize revenue, profit!
+ print "  Total:", revenue, "+", profit!
+
+ // leverage: Multiply by 2 (for maximum impact!)
+ print "\n2. LEVERAGE (doubling for impact):"!
+-const sales = Number(1000)!
++const sales = Number 1000!
+ leverage sales!
+ print "  Leveraged sales: 1000 * 2"!
+
+-const buzz = String("Synergy")!
++const buzz = String "Synergy"!
+ leverage buzz!
+ print "  Leveraged buzzword: Synergy * 2"!
+
+ // paradigm_shift: Negate or reverse
+ print "\n3. PARADIGM SHIFT (complete reversal):"!
+-const oldThinking = Number(100)!
++const oldThinking = Number 100!
+ paradigm_shift oldThinking!
+ print "  Old thinking: 100 -> -100"!
+
+-const direction = String("forward")!
++const direction = String "forward"!
+ paradigm_shift direction!
+ print "  Direction: forward -> backward"!
+
+-const mindset = Boolean(true)!
++const mindset = Boolean true!
+ paradigm_shift mindset!
+ print "  Mindset: true -> false"!
+
+diff --git a/programs/04_satirical/22_satirical_showcase.gom b/programs/04_satirical/22_satirical_showcase.gom
+index 4549a60..2414a4f 100644
+--- a/programs/04_satirical/22_satirical_showcase.gom
++++ b/programs/04_satirical/22_satirical_showcase.gom
+@@ -7,8 +7,8 @@ print "=== The Ultimate Corporate Procrastinator ==="!
+ try {
+    print "\n🏢 QUARTERLY PLANNING SESSION"!
+
+-   const q1_target = Number(1000000)!
+-   const q1_actual = Number(750000)!
++   const q1_target = Number 1000000!
++   const q1_actual = Number 750000!
+
+    synergize q1_target, q1_actual!
+    leverage q1_actual!
+@@ -26,7 +26,7 @@ later {
+    print "  • Update TPS reports"!
+
+    try {
+-      const reports = Number(47)!
++      const reports = Number 47!
+       leverage reports!
+       print "    Leveraged those reports to", reports!
+    } whatever {
+@@ -48,13 +48,13 @@ whenever {
+ print "\n💼 STRATEGIC INITIATIVES:"!
+
+ try {
+-   const oldStrategy = String("reactive")!
++   const oldStrategy = String "reactive"!
+    paradigm_shift oldStrategy!
+    print "Shifted from reactive to proactive approach"!
+
+    later {
+-      const synergy = String("cross-functional")!
+-      const alignment = String("stakeholder")!
++      const synergy = String "cross-functional"!
++      const alignment = String "stakeholder"!
+       synergize synergy, alignment!
+       print "Creating", synergy, alignment, "synergies"!
+    }
+diff --git a/programs/04_satirical/24_superstitious_programming.gom b/programs/04_satirical/24_superstitious_programming.gom
+index f84da72..873c2a8 100644
+--- a/programs/04_satirical/24_superstitious_programming.gom
++++ b/programs/04_satirical/24_superstitious_programming.gom
+@@ -6,7 +6,7 @@ print "=== Superstitious Programming Demo ==="!
+ // Lucky block - good fortune expected
+ lucky {
+    print "Attempting risky operation..."!
+-   const result = Number(42) / Number(2)!
++   const result = Number(42) / Number 2!
+    print "Result:", result!
+ }
+
+@@ -14,7 +14,7 @@ lucky {
+ print "\nCrossing fingers for success..."!
+ cross_fingers {
+    print "This might work, this might not!"!
+-   const magic = Number(777)!
++   const magic = Number 777!
+    print "Magic number:", magic!
+ }
+
+@@ -27,14 +27,14 @@ cross_fingers {
+ print "\nKnocking on wood for protection..."!
+ knock_on_wood {
+    print "This is protected by superstition!"!
+-   const safe = String("safe and sound")!
++   const safe = String "safe and sound"!
+    print safe!
+ }
+
+ // Unlucky block - expect failure
+ unlucky {
+    print "This probably won't work..."!
+-   const doom = Number(13)!
++   const doom = Number 13!
+    print "Doom number:", doom!
+ }
+
+diff --git a/programs/04_satirical/25_ultimate_satire.gom b/programs/04_satirical/25_ultimate_satire.gom
+index 89d2ca0..3531e69 100644
+--- a/programs/04_satirical/25_ultimate_satire.gom
++++ b/programs/04_satirical/25_ultimate_satire.gom
+@@ -8,8 +8,8 @@ happy {
+    print "\n😊 Beginning with positive vibes!"!
+
+    // Corporate speak in happy mode
+-   const team = String("A-Team")!
+-   const project = String("MVP")!
++   const team = String "A-Team"!
++   const project = String "MVP"!
+    synergize team, project!
+    print "Synergized:", team, "with", project!
+ }
+@@ -17,7 +17,7 @@ happy {
+ // Excited about the possibilities
+ excited {
+    print "\n🎉 Super excited to leverage our synergies!"!
+-   leverage String("HYPE")!
++   leverage String "HYPE"!
+ }
+
+ // Procrastinate on important stuff
+@@ -39,7 +39,7 @@ lucky {
+       knock_on_wood {
+          print "Triple protection: Lucky + Crossed Fingers + Knocked Wood!"!
+          print "Deploying..."!
+-         const deploy = String("SUCCESS")!
++         const deploy = String "SUCCESS"!
+          print "Status:", deploy!
+       }
+    }
+@@ -52,7 +52,7 @@ tired {
+ }
+
+ // Paradigm shift the thinking
+-const oldWay = String("waterfall")!
++const oldWay = String "waterfall"!
+ print "\nOld methodology:", oldWay!
+ paradigm_shift oldWay!
+ print "New methodology: paradigm shifted!"!
+diff --git a/programs/04_satirical/26_quantum_programming.gom b/programs/04_satirical/26_quantum_programming.gom
+index 68a3df9..9a0259f 100644
+--- a/programs/04_satirical/26_quantum_programming.gom
++++ b/programs/04_satirical/26_quantum_programming.gom
+@@ -15,7 +15,7 @@ print "   Until we observe it, it's both 1 AND 2 AND 3 AND 4 AND 5!"!
+
+ print ""!
+ print "3. Observing quantum variable (collapses wavefunction)..."!
+-const result = observe("x")!
++const result = observe "x"!
+ print "   Result: ${result}"!
+
+ print ""!
+@@ -31,9 +31,9 @@ quantum c ["cat", "dog", "bird"]!
+
+ print ""!
+ print "6. Observing all quantum states..."!
+-const val_a = observe("a")!
+-const val_b = observe("b")!
+-const val_c = observe("c")!
++const val_a = observe "a"!
++const val_b = observe "b"!
++const val_c = observe "c"!
+
+ print "   a collapsed to: ${val_a}"!
+ print "   b collapsed to: ${val_b}"!
+diff --git a/programs/04_satirical/27_time_travel.gom b/programs/04_satirical/27_time_travel.gom
+index 6e793ac..523acc2 100644
+--- a/programs/04_satirical/27_time_travel.gom
++++ b/programs/04_satirical/27_time_travel.gom
+@@ -20,9 +20,9 @@ print "3. Current value of counter: ${counter}"!
+
+ print ""!
+ print "4. Accessing PAST values..."!
+-const past_1 = past("counter", 1)!
+-const past_3 = past("counter", 3)!
+-const past_5 = past("counter", 5)!
++const past_1 = past "counter", 1!
++const past_3 = past "counter", 3!
++const past_5 = past "counter", 5!
+
+ print "   1 step ago: ${past_1}"!
+ print "   3 steps ago: ${past_3}"!
+@@ -30,14 +30,14 @@ print "   5 steps ago: ${past_5}"!
+
+ print ""!
+ print "5. Predicting the FUTURE..."!
+-const future_val = future("counter")!
++const future_val = future "counter"!
+ print "   Future prediction: ${future_val}"!
+ print "   (Disclaimer: The future is unknowable and random!)"!
+
+ print ""!
+ print "6. Creating a timeline paradox..."!
+ var x 100!
+-const past_x = past("x", 1)!
++const past_x = past "x", 1!
+ print "   Past value that doesn't exist: ${past_x}"!
+ print "   (Returns 0 for non-existent history)"!
+
+@@ -48,10 +48,10 @@ temperature = 22!
+ temperature = 25!
+ temperature = 30!
+
+-const yesterday_temp = past("temperature", 2)!
++const yesterday_temp = past "temperature", 2!
+ print "   Temperature 2 steps ago: ${yesterday_temp}°C"!
+
+-const predicted_temp = future("temperature")!
++const predicted_temp = future "temperature"!
+ print "   Predicted future temperature: ${predicted_temp}°C"!
+
+ print ""!
+diff --git a/programs/04_satirical/28_quantum_time_spectacular.gom b/programs/04_satirical/28_quantum_time_spectacular.gom
+index a3a374f..5adb087 100644
+--- a/programs/04_satirical/28_quantum_time_spectacular.gom
++++ b/programs/04_satirical/28_quantum_time_spectacular.gom
+@@ -8,20 +8,20 @@ print ""!
+ print "Part 1: Quantum Time Travel Paradox"!
+ print "------------------------------------"!
+ quantum timeline [1, 2, 3, 4, 5]!
+-const collapsed_timeline = observe("timeline")!
++const collapsed_timeline = observe "timeline"!
+ print "Timeline collapsed to: ${collapsed_timeline}"!
+
+-const past_timeline = past("collapsed_timeline", 1)!
++const past_timeline = past "collapsed_timeline", 1!
+ print "But in the past, timeline was: ${past_timeline}"!
+
+ print ""!
+ print "Part 2: Superposition of Futures"!
+ print "---------------------------------"!
+ quantum future_paths ["success", "failure", "maybe"]!
+-const chosen_path = observe("future_paths")!
++const chosen_path = observe "future_paths"!
+ print "The universe chose: ${chosen_path}"!
+
+-const predicted = future("chosen_path")!
++const predicted = future "chosen_path"!
+ print "But the future predicts: ${predicted}"!
+
+ print ""!
+@@ -30,7 +30,7 @@ print "---------------------------------"!
+
+ happy {
+    quantum mood ["joyful", "ecstatic", "content"]!
+-   const current_mood = observe("mood")!
++   const current_mood = observe "mood"!
+    print "😊 In a happy state, mood is: ${current_mood}"!
+ }
+
+@@ -40,7 +40,7 @@ print "-------------------------------"!
+
+ lucky {
+    quantum lottery [7, 13, 42, 99]!
+-   const winning_number = observe("lottery")!
++   const winning_number = observe "lottery"!
+    print "🍀 Your lucky number is: ${winning_number}!"!
+ }
+
+@@ -54,7 +54,7 @@ emotion = "excited"!
+ emotion = "tired"!
+
+ excited {
+-   const past_emotion = past("emotion", 2)!
++   const past_emotion = past "emotion", 2!
+    print "🎉 Two emotional states ago, we were: ${past_emotion}!"!
+ }
+
+@@ -64,10 +64,10 @@ print "-----------------------------"!
+
+ quantum reality ["real", "simulation", "dream", "maybe"]!
+ cross_fingers {
+-   const our_reality = observe("reality")!
++   const our_reality = observe "reality"!
+    print "🤞 We live in: ${our_reality}"!
+
+-   const future_reality = future("our_reality")!
++   const future_reality = future "our_reality"!
+    print "🔮 Future reality prediction: ${future_reality}"!
+ }
+
+diff --git a/programs/05_analysis/36_base_numbers.gom b/programs/05_analysis/36_base_numbers.gom
+index 07bb624..20fed22 100644
+--- a/programs/05_analysis/36_base_numbers.gom
++++ b/programs/05_analysis/36_base_numbers.gom
+@@ -10,31 +10,31 @@ print "------------------------------"!
+ const decimal = 42!
+ print "Decimal: ${decimal}"!
+
+-const binary = to_binary(decimal)!
++const binary = to_binary decimal!
+ print "Binary (base 2): ${binary}"!
+
+-const octal = to_octal(decimal)!
++const octal = to_octal decimal!
+ print "Octal (base 8): ${octal}"!
+
+-const hex = to_hex(decimal)!
++const hex = to_hex decimal!
+ print "Hexadecimal (base 16): ${hex}"!
+
+-const base5 = to_base(decimal, 5)!
++const base5 = to_base decimal, 5!
+ print "Base 5: ${base5}"!
+
+ print ""!
+ print "Part 2: Converting Back to Decimal"!
+ print "-----------------------------------"!
+-const from_bin = from_binary("101010")!
++const from_bin = from_binary "101010"!
+ print "Binary '101010' to decimal: ${from_bin}"!
+
+-const from_oct = from_octal("52")!
++const from_oct = from_octal "52"!
+ print "Octal '52' to decimal: ${from_oct}"!
+
+-const from_h = from_hex("2A")!
++const from_h = from_hex "2A"!
+ print "Hex '2A' to decimal: ${from_h}"!
+
+-const from_b5 = from_base("132", 5)!
++const from_b5 = from_base "132", 5!
+ print "Base 5 '132' to decimal: ${from_b5}"!
+
+ print ""!
+@@ -43,16 +43,16 @@ print "-----------------------------------"!
+ const num = 255!
+ print "Converting ${num} to different bases:"!
+
+-const base3 = to_base(num, 3)!
++const base3 = to_base num, 3!
+ print "  Base 3: ${base3}"!
+
+-const base7 = to_base(num, 7)!
++const base7 = to_base num, 7!
+ print "  Base 7: ${base7}"!
+
+-const base12 = to_base(num, 12)!
++const base12 = to_base num, 12!
+ print "  Base 12: ${base12}"!
+
+-const base36 = to_base(num, 36)!
++const base36 = to_base num, 36!
+ print "  Base 36: ${base36}"!
+
+ print ""!
+@@ -61,28 +61,28 @@ print "------------------------------"!
+ print "Adding binary and hex, result in octal:"!
+ const bin_num = "1010"!  // 10 in decimal
+ const hex_num = "14"!    // 20 in decimal
+-const sum_oct = base_add(bin_num, 2, hex_num, 16, 8)!
++const sum_oct = base_add bin_num, 2, hex_num, 16, 8!
+ print "  Binary ${bin_num} + Hex ${hex_num} = Octal ${sum_oct}"!
+
+ print ""!
+ print "Subtracting in different bases:"!
+ const oct_a = "100"!  // 64 in decimal
+ const dec_b = 14!
+-const diff_bin = base_sub(oct_a, 8, dec_b, 10, 2)!
++const diff_bin = base_sub oct_a, 8, dec_b, 10, 2!
+ print "  Octal ${oct_a} - Decimal ${dec_b} = Binary ${diff_bin}"!
+
+ print ""!
+ print "Multiplying across bases:"!
+ const base5_x = "23"!  // 13 in decimal
+ const base7_y = "12"!  // 9 in decimal
+-const product_hex = base_mul(base5_x, 5, base7_y, 7, 16)!
++const product_hex = base_mul base5_x, 5, base7_y, 7, 16!
+ print "  Base5 ${base5_x} * Base7 ${base7_y} = Hex ${product_hex}"!
+
+ print ""!
+ print "Division with different bases:"!
+ const hex_dividend = "64"!  // 100 in decimal
+ const bin_divisor = "101"!  // 5 in decimal
+-const quotient_oct = base_div(hex_dividend, 16, bin_divisor, 2, 8)!
++const quotient_oct = base_div hex_dividend, 16, bin_divisor, 2, 8!
+ print "  Hex ${hex_dividend} / Binary ${bin_divisor} = Octal ${quotient_oct}"!
+
+ print ""!
+@@ -91,13 +91,13 @@ print "----------------------------------"!
+ print "Calculate Fibonacci in base 7:"!
+ var a = 0!
+ var b = 1!
+-print "F(0) = ${to_base(a, 7)}"!
+-print "F(1) = ${to_base(b, 7)}"!
++print "F(0) = ${to_base a, 7}"!
++print "F(1) = ${to_base b, 7}"!
+
+ var i = 2!
+ when i < 10 {
+    const next = a + b!
+-   print "F(${i}) = ${to_base(next, 7)}"!
++   print "F(${i}) = ${to_base next, 7}"!
+    a = b!
+    b = next!
+    i = i + 1!
+@@ -111,10 +111,10 @@ print "-------|------|-----|-----|-----|----"!
+
+ var n = 0!
+ when n < 17 {
+-   const b2 = to_binary(n)!
+-   const b8 = to_octal(n)!
+-   const b16 = to_hex(n)!
+-   const b36 = to_base(n, 36)!
++   const b2 = to_binary n!
++   const b8 = to_octal n!
++   const b16 = to_hex n!
++   const b36 = to_base n, 36!
+    print "${n}      | ${b2}  | ${b8}   | ${n}   | ${b16}   | ${b36}"!
+    n = n + 1!
+ }!
+diff --git a/programs/05_analysis/37_base_simple.gom b/programs/05_analysis/37_base_simple.gom
+index d7c8f3a..cc75808 100644
+--- a/programs/05_analysis/37_base_simple.gom
++++ b/programs/05_analysis/37_base_simple.gom
+@@ -6,10 +6,10 @@ print ""!
+
+ // Test basic conversions
+ print "Convert 42 to different bases:"!
+-print "Binary: ${to_binary(42)}"!
+-print "Octal: ${to_octal(42)}"!
+-print "Hex: ${to_hex(42)}"!
+-print "Base 5: ${to_base(42, 5)}"!
++print "Binary: ${to_binary 42}"!
++print "Octal: ${to_octal 42}"!
++print "Hex: ${to_hex 42}"!
++print "Base 5: ${to_base 42, 5}"!
+ print ""!
+
+ // Test conversions back to decimal
+@@ -18,34 +18,34 @@ const bin_str = "101010"!
+ const oct_str = "52"!
+ const hex_str = "2A"!
+ const b5_str = "132"!
+-print "Binary 101010 = ${from_binary(bin_str)}"!
+-print "Octal 52 = ${from_octal(oct_str)}"!
+-print "Hex 2A = ${from_hex(hex_str)}"!
+-print "Base 5 '132' = ${from_base(b5_str, 5)}"!
++print "Binary 101010 = ${from_binary bin_str}"!
++print "Octal 52 = ${from_octal oct_str}"!
++print "Hex 2A = ${from_hex hex_str}"!
++print "Base 5 '132' = ${from_base b5_str, 5}"!
+ print ""!
+
+ // Test cross-base arithmetic
+ print "Cross-base arithmetic:"!
+-const add_result = base_add("1010", 2, "14", 16, 8)!
++const add_result = base_add "1010", 2, "14", 16, 8!
+ print "Binary 1010 + Hex 14 (in octal) = ${add_result}"!
+-const sub_result = base_sub("100", 8, 14, 10, 2)!
++const sub_result = base_sub "100", 8, 14, 10, 2!
+ print "Octal 100 - Decimal 14 (in binary) = ${sub_result}"!
+-const mul_result = base_mul("23", 5, "12", 7, 16)!
++const mul_result = base_mul "23", 5, "12", 7, 16!
+ print "Base5 23 * Base7 12 (in hex) = ${mul_result}"!
+-const div_result = base_div("64", 16, "101", 2, 8)!
++const div_result = base_div "64", 16, "101", 2, 8!
+ print "Hex 64 / Binary 101 (in octal) = ${div_result}"!
+ print ""!
+
+ // Test edge cases
+ print "Edge cases:"!
+-const zero_b2 = to_base(0, 2)!
++const zero_b2 = to_base 0, 2!
+ print "Zero in base 2: ${zero_b2}"!
+-const zero_b36 = to_base(0, 36)!
++const zero_b36 = to_base 0, 36!
+ print "Zero in base 36: ${zero_b36}"!
+-const n255_b36 = to_base(255, 36)!
++const n255_b36 = to_base 255, 36!
+ print "255 in base 36: ${n255_b36}"!
+ const zz_str = "ZZ"!
+-const zz_dec = from_base(zz_str, 36)!
++const zz_dec = from_base zz_str, 36!
+ print "Base 36 'ZZ' to decimal: ${zz_dec}"!
+ print ""!
+
+diff --git a/programs/05_analysis/38_base_practical.gom b/programs/05_analysis/38_base_practical.gom
+index 3f0ea71..3190d65 100644
+--- a/programs/05_analysis/38_base_practical.gom
++++ b/programs/05_analysis/38_base_practical.gom
+@@ -13,10 +13,10 @@ const ip_oct2 = 168!
+ const ip_oct3 = 1!
+ const ip_oct4 = 254!
+
+-const bin1 = to_binary(ip_oct1)!
+-const bin2 = to_binary(ip_oct2)!
+-const bin3 = to_binary(ip_oct3)!
+-const bin4 = to_binary(ip_oct4)!
++const bin1 = to_binary ip_oct1!
++const bin2 = to_binary ip_oct2!
++const bin3 = to_binary ip_oct3!
++const bin4 = to_binary ip_oct4!
+
+ print "IP Address: ${ip_oct1}.${ip_oct2}.${ip_oct3}.${ip_oct4}"!
+ print "Binary: ${bin1}.${bin2}.${bin3}.${bin4}"!
+@@ -29,9 +29,9 @@ const red = 255!
+ const green = 99!
+ const blue = 71!
+
+-const hex_r = to_hex(red)!
+-const hex_g = to_hex(green)!
+-const hex_b = to_hex(blue)!
++const hex_r = to_hex red!
++const hex_g = to_hex green!
++const hex_b = to_hex blue!
+
+ print "RGB: (${red}, ${green}, ${blue})"!
+ print "Hex color: #${hex_r}${hex_g}${hex_b}"!
+@@ -44,8 +44,8 @@ const owner_rwx = 7!  // read=4, write=2, execute=1
+ const group_rx = 5!   // read=4, execute=1
+ const other_r = 4!    // read=4
+
+-const perm_oct = to_octal(owner_rwx * 64 + group_rx * 8 + other_r)!
+-const perm_bin = to_binary(owner_rwx * 64 + group_rx * 8 + other_r)!
++const perm_oct = to_octal owner_rwx * 64 + group_rx * 8 + other_r!
++const perm_bin = to_binary owner_rwx * 64 + group_rx * 8 + other_r!
+
+ print "Permissions: ${owner_rwx}${group_rx}${other_r} (octal)"!
+ print "Full octal: ${perm_oct}"!
+@@ -57,8 +57,8 @@ print ""!
+ print "4. Memory Address Conversion"!
+ print "-----------------------------"!
+ const mem_addr = 65535!
+-const mem_hex = to_hex(mem_addr)!
+-const mem_bin = to_binary(mem_addr)!
++const mem_hex = to_hex mem_addr!
++const mem_bin = to_binary mem_addr!
+
+ print "Decimal address: ${mem_addr}"!
+ print "Hex: 0x${mem_hex}"!
+@@ -69,10 +69,10 @@ print ""!
+ print "5. Custom Base Encoding"!
+ print "-----------------------"!
+ const data = 12345!
+-const base32 = to_base(data, 32)!
++const base32 = to_base data, 32!
+ print "Data: ${data}"!
+ print "Base-32 encoded: ${base32}"!
+-const decoded = from_base(base32, 32)!
++const decoded = from_base base32, 32!
+ print "Decoded back: ${decoded}"!
+ print ""!
+
+@@ -82,9 +82,9 @@ print "--------------"!
+ const bin_a = "1111"!  // 15 in decimal
+ const bin_b = "1010"!  // 10 in decimal
+
+-const sum_bin = base_add(bin_a, 2, bin_b, 2, 2)!
+-const diff_bin = base_sub(bin_a, 2, bin_b, 2, 2)!
+-const prod_bin = base_mul(bin_a, 2, bin_b, 2, 2)!
++const sum_bin = base_add bin_a, 2, bin_b, 2, 2!
++const diff_bin = base_sub bin_a, 2, bin_b, 2, 2!
++const prod_bin = base_mul bin_a, 2, bin_b, 2, 2!
+
+ print "Binary ${bin_a} + ${bin_b} = ${sum_bin}"!
+ print "Binary ${bin_a} - ${bin_b} = ${diff_bin}"!
+@@ -96,8 +96,8 @@ print "7. Check Powers of 2"!
+ print "--------------------"!
+ const num16 = 16!
+ const num20 = 20!
+-const bin16 = to_binary(num16)!
+-const bin20 = to_binary(num20)!
++const bin16 = to_binary num16!
++const bin20 = to_binary num20!
+
+ print "${num16} in binary: ${bin16} (power of 2!)"!
+ print "${num20} in binary: ${bin20} (not power of 2)"!
+diff --git a/programs/05_analysis/39_statistics.gom b/programs/05_analysis/39_statistics.gom
+index fcb9ecc..60561c8 100644
+--- a/programs/05_analysis/39_statistics.gom
++++ b/programs/05_analysis/39_statistics.gom
+@@ -14,29 +14,29 @@ print ""!
+ // Basic statistics
+ print "1. Measures of Central Tendency"!
+ print "--------------------------------"!
+-const avg = mean(scores)!
++const avg = mean scores!
+ print "Mean (Average): ${avg}"!
+
+-const mid = median(scores)!
++const mid = median scores!
+ print "Median (Middle): ${mid}"!
+
+-const most_common = mode(scores)!
++const most_common = mode scores!
+ print "Mode (Most frequent): ${most_common}"!
+ print ""!
+
+ // Measures of spread
+ print "2. Measures of Variability"!
+ print "---------------------------"!
+-const var = variance(scores)!
++const var = variance scores!
+ print "Variance: ${var}"!
+
+-const sd = stdev(scores)!
++const sd = stdev scores!
+ print "Standard Deviation: ${sd}"!
+
+-const min_score = min_val(scores)!
++const min_score = min_val scores!
+ print "Minimum: ${min_score}"!
+
+-const max_score = max_val(scores)!
++const max_score = max_val scores!
+ print "Maximum: ${max_score}"!
+
+ const range_val = max_score - min_score!
+@@ -46,16 +46,16 @@ print ""!
+ // Percentiles
+ print "3. Percentile Analysis"!
+ print "----------------------"!
+-const p25 = percentile(scores, 25)!
++const p25 = percentile scores, 25!
+ print "25th Percentile (Q1): ${p25}"!
+
+-const p50 = percentile(scores, 50)!
++const p50 = percentile scores, 50!
+ print "50th Percentile (Median): ${p50}"!
+
+-const p75 = percentile(scores, 75)!
++const p75 = percentile scores, 75!
+ print "75th Percentile (Q3): ${p75}"!
+
+-const p90 = percentile(scores, 90)!
++const p90 = percentile scores, 90!
+ print "90th Percentile: ${p90}"!
+ print ""!
+
+@@ -66,7 +66,7 @@ const study_hours = [-1, 5, 8, 3, 7, 6, 9, 4, 7, 6, 7]!
+ print "Study Hours: ${study_hours}"!
+ print "Test Scores: ${scores}"!
+
+-const corr = correlation(study_hours, scores)!
++const corr = correlation study_hours, scores!
+ print "Correlation coefficient: ${corr}"!
+ print "(1 = perfect positive, -1 = perfect negative)"!
+ print ""!
+@@ -77,16 +77,16 @@ print "------------------------------"!
+ const monthly_sales = [-1, 12000, 15000, 13500, 18000, 16500, 19000, 17200, 20000, 18500, 21000, 19500, 22000]!
+ print "Monthly Sales (12 months): ${monthly_sales}"!
+
+-const avg_sales = mean(monthly_sales)!
++const avg_sales = mean monthly_sales!
+ print "Average Monthly Sales: $${avg_sales}"!
+
+-const median_sales = median(monthly_sales)!
++const median_sales = median monthly_sales!
+ print "Median Sales: $${median_sales}"!
+
+-const sales_sd = stdev(monthly_sales)!
++const sales_sd = stdev monthly_sales!
+ print "Standard Deviation: $${sales_sd}"!
+
+-const total_sales = sum_list(monthly_sales)!
++const total_sales = sum_list monthly_sales!
+ print "Total Annual Sales: $${total_sales}"!
+ print ""!
+
+diff --git a/programs/05_analysis/40_financial.gom b/programs/05_analysis/40_financial.gom
+index 96ea6f5..49b506e 100644
+--- a/programs/05_analysis/40_financial.gom
++++ b/programs/05_analysis/40_financial.gom
+@@ -13,7 +13,7 @@ const annual_rate = 0.05!  // 5%
+ const years = 10!
+ const compounds_per_year = 12!  // Monthly compounding
+
+-const final_amount = compound_interest(principal, annual_rate, years, compounds_per_year)!
++const final_amount = compound_interest principal, annual_rate, years, compounds_per_year!
+ print "Principal: $${principal}"!
+ print "Annual Rate: ${annual_rate * 100}%"!
+ print "Time: ${years} years"!
+@@ -30,7 +30,7 @@ const simple_principal = 5000!
+ const simple_rate = 0.04!  // 4%
+ const simple_time = 3!
+
+-const simple_int = simple_interest(simple_principal, simple_rate, simple_time)!
++const simple_int = simple_interest simple_principal, simple_rate, simple_time!
+ print "Principal: $${simple_principal}"!
+ print "Rate: ${simple_rate * 100}%"!
+ print "Time: ${simple_time} years"!
+@@ -46,7 +46,7 @@ const loan_amount = 250000!  // $250k mortgage
+ const monthly_rate = 0.045 / 12!  // 4.5% annual / 12 months
+ const num_payments = 30 * 12!  // 30 years * 12 months
+
+-const monthly_payment = pmt(monthly_rate, num_payments, loan_amount)!
++const monthly_payment = pmt monthly_rate, num_payments, loan_amount!
+ print "Loan Amount: $${loan_amount}"!
+ print "Annual Rate: 4.5%"!
+ print "Loan Term: 30 years"!
+@@ -64,7 +64,7 @@ const monthly_investment = 500!
+ const inv_rate = 0.07 / 12!  // 7% annual
+ const inv_months = 20 * 12!  // 20 years
+
+-const future_value = fv(inv_rate, inv_months, -monthly_investment, 0)!
++const future_value = fv inv_rate, inv_months, -monthly_investment, 0!
+ print "Monthly Investment: $${monthly_investment}"!
+ print "Annual Return: 7%"!
+ print "Time Period: 20 years"!
+@@ -78,7 +78,7 @@ const future_needed = 100000!
+ const pv_rate = 0.06 / 12!
+ const pv_months = 10 * 12!
+
+-const monthly_needed = pv(pv_rate, pv_months, -future_needed / pv_months)!
++const monthly_needed = pv pv_rate, pv_months, -future_needed / pv_months!
+ print "Future Value Needed: $${future_needed}"!
+ print "Annual Rate: 6%"!
+ print "Time: 10 years"!
+@@ -94,7 +94,7 @@ print "Initial Investment: $50,000"!
+ print "Annual Cash Flows: $15k, $18k, $20k, $22k, $25k"!
+ print "Discount Rate: ${discount_rate * 100}%"!
+
+-const npv_result = npv(discount_rate, cash_flows)!
++const npv_result = npv discount_rate, cash_flows!
+ print "Net Present Value: $${npv_result}"!
+
+ if npv_result > 0 {
+@@ -115,7 +115,7 @@ const monthly_contribution = 1000!
+ const expected_return = 0.08 / 12!
+
+ const retirement_months = retirement_years * 12!
+-const retirement_fund = fv(expected_return, retirement_months, -monthly_contribution, 0)!
++const retirement_fund = fv expected_return, retirement_months, -monthly_contribution, 0!
+ print "Current Age: ${current_age}"!
+ print "Retirement Age: ${retirement_age}"!
+ print "Monthly Contribution: $${monthly_contribution}"!
+diff --git a/programs/05_analysis/41_business.gom b/programs/05_analysis/41_business.gom
+index fd64505..97177db 100644
+--- a/programs/05_analysis/41_business.gom
++++ b/programs/05_analysis/41_business.gom
+@@ -11,7 +11,7 @@ print "------------------------------"!
+ const marketing_cost = 50000!
+ const revenue_generated = 150000!
+
+-const roi_pct = roi(revenue_generated, marketing_cost)!
++const roi_pct = roi revenue_generated, marketing_cost!
+ print "Marketing Campaign Analysis:"!
+ print "Investment: $${marketing_cost}"!
+ print "Revenue Generated: $${revenue_generated}"!
+@@ -21,11 +21,11 @@ print ""!
+ // Different investment comparison
+ const invest_a_cost = 100000!
+ const invest_a_gain = 125000!
+-const roi_a = roi(invest_a_gain, invest_a_cost)!
++const roi_a = roi invest_a_gain, invest_a_cost!
+
+ const invest_b_cost = 50000!
+ const invest_b_gain = 70000!
+-const roi_b = roi(invest_b_gain, invest_b_cost)!
++const roi_b = roi invest_b_gain, invest_b_cost!
+
+ print "Investment Comparison:"!
+ print "Option A - Cost: $${invest_a_cost}, Gain: $${invest_a_gain}, ROI: ${roi_a}%"!
+@@ -38,7 +38,7 @@ print "-------------------------"!
+ const product_revenue = 500000!
+ const product_cost = 350000!
+
+-const margin = profit_margin(product_revenue, product_cost)!
++const margin = profit_margin product_revenue, product_cost!
+ print "Product Line Performance:"!
+ print "Revenue: $${product_revenue}"!
+ print "Cost: $${product_cost}"!
+@@ -49,17 +49,17 @@ print ""!
+ print "Product Comparison:"!
+ const p1_rev = 100000!
+ const p1_cost = 70000!
+-const p1_margin = profit_margin(p1_rev, p1_cost)!
++const p1_margin = profit_margin p1_rev, p1_cost!
+ print "Product 1 - Margin: ${p1_margin}%"!
+
+ const p2_rev = 80000!
+ const p2_cost = 50000!
+-const p2_margin = profit_margin(p2_rev, p2_cost)!
++const p2_margin = profit_margin p2_rev, p2_cost!
+ print "Product 2 - Margin: ${p2_margin}%"!
+
+ const p3_rev = 120000!
+ const p3_cost = 95000!
+-const p3_margin = profit_margin(p3_rev, p3_cost)!
++const p3_margin = profit_margin p3_rev, p3_cost!
+ print "Product 3 - Margin: ${p3_margin}%"!
+ print ""!
+
+@@ -70,7 +70,7 @@ const year_2020_revenue = 1000000!
+ const year_2025_revenue = 2500000!
+ const years_elapsed = 5!
+
+-const growth_rate = cagr(year_2020_revenue, year_2025_revenue, years_elapsed)!
++const growth_rate = cagr year_2020_revenue, year_2025_revenue, years_elapsed!
+ print "Company Growth Analysis:"!
+ print "2020 Revenue: $${year_2020_revenue}"!
+ print "2025 Revenue: $${year_2025_revenue}"!
+@@ -83,7 +83,7 @@ print "Market Expansion Analysis:"!
+ const market_2022 = 500000!
+ const market_2025 = 950000!
+ const market_years = 3!
+-const market_cagr = cagr(market_2022, market_2025, market_years)!
++const market_cagr = cagr market_2022, market_2025, market_years!
+ print "Market Size 2022: $${market_2022}"!
+ print "Market Size 2025: $${market_2025}"!
+ print "Growth Rate: ${market_cagr}%"!
+@@ -96,7 +96,7 @@ const fixed_costs = 100000!  // Rent, salaries, etc
+ const price_per_unit = 50!
+ const variable_cost = 30!  // Materials, labor per unit
+
+-const breakeven_units = break_even(fixed_costs, price_per_unit, variable_cost)!
++const breakeven_units = break_even fixed_costs, price_per_unit, variable_cost!
+ print "Business Break-Even Analysis:"!
+ print "Fixed Costs: $${fixed_costs}"!
+ print "Price per Unit: $${price_per_unit}"!
+@@ -113,15 +113,15 @@ const fixed = 50000!
+ const var_cost = 20!
+
+ const scenario1_price = 35!
+-const be1 = break_even(fixed, scenario1_price, var_cost)!
++const be1 = break_even fixed, scenario1_price, var_cost!
+ print "Price $${scenario1_price}: Need ${be1} units"!
+
+ const scenario2_price = 45!
+-const be2 = break_even(fixed, scenario2_price, var_cost)!
++const be2 = break_even fixed, scenario2_price, var_cost!
+ print "Price $${scenario2_price}: Need ${be2} units"!
+
+ const scenario3_price = 60!
+-const be3 = break_even(fixed, scenario3_price, var_cost)!
++const be3 = break_even fixed, scenario3_price, var_cost!
+ print "Price $${scenario3_price}: Need ${be3} units"!
+ print ""!
+
+@@ -140,7 +140,7 @@ const q4_cost = 215000!
+ const total_revenue = q1_revenue + q2_revenue + q3_revenue + q4_revenue!
+ const total_cost = q1_cost + q2_cost + q3_cost + q4_cost!
+ const annual_profit = total_revenue - total_cost!
+-const annual_margin = profit_margin(total_revenue, total_cost)!
++const annual_margin = profit_margin total_revenue, total_cost!
+
+ print "Annual Performance:"!
+ print "Total Revenue: $${total_revenue}"!
+@@ -150,7 +150,7 @@ print "Profit Margin: ${annual_margin}%"!
+
+ const investment = total_cost!
+ const return_val = total_revenue!
+-const annual_roi = roi(return_val, investment)!
++const annual_roi = roi return_val, investment!
+ print "ROI: ${annual_roi}%"!
+ print ""!
+
+diff --git a/programs/05_analysis/42_scientific.gom b/programs/05_analysis/42_scientific.gom
+index 1c52297..2f34ba3 100644
+--- a/programs/05_analysis/42_scientific.gom
++++ b/programs/05_analysis/42_scientific.gom
+@@ -14,7 +14,7 @@ const y_data = [-1, 2.1, 4.2, 5.9, 8.1, 10.0, 12.2, 13.9, 16.1, 18.0, 20.2]!
+ print "X values: ${x_data}"!
+ print "Y values: ${y_data}"!
+
+-const regression = linear_regression(x_data, y_data)!
++const regression = linear_regression x_data, y_data!
+ const slope = regression[-1]!
+ const intercept = regression[0]!
+
+@@ -27,11 +27,11 @@ print ""!
+ print "2. Predictions Using Regression"!
+ print "--------------------------------"!
+ const x_predict1 = 15!
+-const y_predict1 = predict(x_predict1, slope, intercept)!
++const y_predict1 = predict x_predict1, slope, intercept!
+ print "Predict y when x = ${x_predict1}: y = ${y_predict1}"!
+
+ const x_predict2 = 20!
+-const y_predict2 = predict(x_predict2, slope, intercept)!
++const y_predict2 = predict x_predict2, slope, intercept!
+ print "Predict y when x = ${x_predict2}: y = ${y_predict2}"!
+ print ""!
+
+@@ -41,14 +41,14 @@ print "Temperature (°F): ${x_data}"!
+ const sales = [-1, 150, 210, 280, 340, 420, 480, 550, 610, 680, 750]!
+ print "Ice Cream Sales ($): ${sales}"!
+
+-const sales_regression = linear_regression(x_data, sales)!
++const sales_regression = linear_regression x_data, sales!
+ const sales_slope = sales_regression[-1]!
+ const sales_intercept = sales_regression[0]!
+
+ print "Sales Model: Sales = ${sales_slope} × Temp + ${sales_intercept}"!
+
+ const temp_95 = 12!
+-const predicted_sales = predict(temp_95, sales_slope, sales_intercept)!
++const predicted_sales = predict temp_95, sales_slope, sales_intercept!
+ print "Predicted sales at 95°F: $${predicted_sales}"!
+ print ""!
+
+@@ -59,7 +59,7 @@ const func_values = [-1, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]!  // x^2
+ print "Function values (x²): ${func_values}"!
+ const step_size = 1!
+
+-const derivatives = derivative(func_values, step_size)!
++const derivatives = derivative func_values, step_size!
+ print "Derivatives (rate of change): ${derivatives}"!
+ print "These approximate 2x at each point"!
+ print ""!
+@@ -69,7 +69,7 @@ print "Physics Example: Position to Velocity"!
+ const positions = [-1, 0, 5, 20, 45, 80, 125, 180, 245]!  // meters
+ print "Position (m) at each second: ${positions}"!
+ const time_step = 1!
+-const velocities = derivative(positions, time_step)!
++const velocities = derivative positions, time_step!
+ print "Velocity (m/s): ${velocities}"!
+ print ""!
+
+@@ -80,7 +80,7 @@ const heights = [-1, 1, 1.4142, 1.7321, 2, 2.2361, 2.4495, 2.6458, 2.8284, 3]!
+ print "Function values (√x): ${heights}"!
+ const dx = 1!
+
+-const area = integrate(heights, dx)!
++const area = integrate heights, dx!
+ print "Approximate area under curve: ${area}"!
+ print ""!
+
+@@ -89,7 +89,7 @@ print "Physics Example: Velocity to Distance"!
+ const velocity_data = [-1, 10, 15, 20, 25, 30, 35, 40, 45, 50]!  // m/s
+ print "Velocity (m/s) each second: ${velocity_data}"!
+ const dt = 1!
+-const distance = integrate(velocity_data, dt)!
++const distance = integrate velocity_data, dt!
+ print "Total distance traveled: ${distance} meters"!
+ print ""!
+
+@@ -101,7 +101,7 @@ const a_coef = 2!
+ const b_coef = -7!
+ const c_coef = 3!
+
+-const roots = quadratic_solve(a_coef, b_coef, c_coef)!
++const roots = quadratic_solve a_coef, b_coef, c_coef!
+ const root1 = roots[-1]!
+ const root2 = roots[0]!
+
+@@ -117,7 +117,7 @@ const grav_a = -4.9!
+ const init_vel = 20!
+ const init_height = 1.5!
+
+-const time_roots = quadratic_solve(grav_a, init_vel, init_height)!
++const time_roots = quadratic_solve grav_a, init_vel, init_height!
+ const t1 = time_roots[-1]!
+ const t2 = time_roots[0]!
+
+@@ -135,7 +135,7 @@ print "6. Engineering Applications"!
+ print "----------------------------"!
+ print "Optimal dimensions for a container:"!
+ print "Solve: x² - 5x - 6 = 0"!
+-const container_roots = quadratic_solve(1, -5, -6)!
++const container_roots = quadratic_solve 1, -5, -6!
+ const dim1 = container_roots[-1]!
+ const dim2 = container_roots[0]!
+ print "Dimension solutions: ${dim1}, ${dim2}"!
+diff --git a/programs/demos/async_pipeline.gom b/programs/demos/async_pipeline.gom
+index 6add0ce..0a4feb3 100644
+--- a/programs/demos/async_pipeline.gom
++++ b/programs/demos/async_pipeline.gom
+@@ -22,15 +22,15 @@ print "=== Async Data Pipeline Demo ==="!
+ print ""!
+
+ const source = "API endpoint"!
+-const rawData = await fetchData(source)!
++const rawData = await fetchData source!
+ print "Raw data: ${rawData}"!
+ print ""!
+
+-const processed = await processData(rawData)!
++const processed = await processData rawData!
+ print "Processed data: ${processed}"!
+ print ""!
+
+-const isValid = await validateData(processed)!
++const isValid = await validateData processed!
+ print "Validation result: ${isValid}"!
+ print ""!
+
+diff --git a/programs/demos/banking_system.gom b/programs/demos/banking_system.gom
+index 8a47696..3f51859 100644
+--- a/programs/demos/banking_system.gom
++++ b/programs/demos/banking_system.gom
+@@ -50,5 +50,5 @@ aliceAccount.transfer 150, bobAccount!
+
+ print ""!
+ print "Final balances:"!
+-print "Alice: ${aliceAccount.getBalance()}"!
+-print "Bob: ${bobAccount.getBalance()}"!
++print "Alice: ${aliceAccount.getBalance }"!
++print "Bob: ${bobAccount.getBalance }"!
+diff --git a/programs/demos/calculator.gom b/programs/demos/calculator.gom
+index cb10f33..9b512d1 100644
+--- a/programs/demos/calculator.gom
++++ b/programs/demos/calculator.gom
+@@ -14,11 +14,11 @@ const y = 3!
+ print "Numbers: x = ${x}, y = ${y}"!
+ print ""!
+
+-print "Addition: ${x} + ${y} = ${add(x, y}")!
+-print "Subtraction: ${x} - ${y} = ${subtract(x, y}")!
+-print "Multiplication: ${x} * ${y} = ${multiply(x, y}")!
+-print "Division: ${x} / ${y} = ${divide(x, y}")!
+-print "Power: ${x} ^ ${y} = ${power(x, y}")!
++print "Addition: ${x} + ${y} = ${add x, y}"!
++print "Subtraction: ${x} - ${y} = ${subtract x, y}"!
++print "Multiplication: ${x} * ${y} = ${multiply x, y}"!
++print "Division: ${x} / ${y} = ${divide x, y}"!
++print "Power: ${x} ^ ${y} = ${power x, y}"!
+
+ print ""!
+-print "Complex expression: (${x} + ${y} * 2 = ${(x + y) * 2}")!
++print "Complex expression: (${x} + ${y} * 2 = ${(x + y) * 2})"!
+diff --git a/programs/demos/feature_showcase.gom b/programs/demos/feature_showcase.gom
+index 8b60448..16fd5a4 100644
+--- a/programs/demos/feature_showcase.gom
++++ b/programs/demos/feature_showcase.gom
+@@ -7,8 +7,8 @@ print ""!
+ print "1. Arrays start at -1"!
+ const arr = [10, 20, 30]!
+ print "   arr = ${arr}"!
+-print "   arr[-1] = ${arr[-1]} (first element")!
+-print "   arr[0] = ${arr[0]} (second element")!
++print "   arr[-1] = ${arr[-1]} (first element)"!
++print "   arr[0] = ${arr[0]} (second element)"!
+ print ""!
+
+ // 2. Fractional indexing
+@@ -38,15 +38,15 @@ print ""!
+ print "5. Multiple Equality Operators"!
+ const a = 42!
+ const b = 42.0!
+-print "   42 = 42.0: ${a = b} (approximate")!
+-print "   42 == 42.0: ${a == b} (standard")!
+-print "   42 === 42.0: ${a === b} (strict")!
++print "   42 = 42.0: ${a = b} (approximate)"!
++print "   42 == 42.0: ${a == b} (standard)"!
++print "   42 === 42.0: ${a === b} (strict)"!
+ print ""!
+
+ // 6. Functions
+ print "6. Functions"!
+ fn add(x, y) => x + y!
+-print "   add(5, 3 = ${add 5, 3}")!
++print "   add(5, 3) = ${add 5, 3}"!
+ print ""!
+
+ // 7. Classes
+diff --git a/programs/demos/grand_deluxe_demo.gom b/programs/demos/grand_deluxe_demo.gom
+index 2eaddea..f540067 100644
+--- a/programs/demos/grand_deluxe_demo.gom
++++ b/programs/demos/grand_deluxe_demo.gom
+@@ -44,8 +44,8 @@ print n[-1]!
+ var s = "GOM"!
+ print "String before push/pop:"!
+ print s!
+-s.push("! ")!
+-s.push("Rocks")!
++s.push "! "!
++s.push "Rocks"!
+ print "String after pushes:"!
+ print s!
+ print "Popped char:"!
+@@ -54,7 +54,7 @@ print "String now:"!
+ print s!
+
+ // 4) Maps (dictionaries)
+-const person = Map()!
++const person = Map!
+ person["name"] = "Ada"!
+ person["age"] = 36!
+ person["skills"] = ["math", "logic", "computing"]!
+@@ -86,7 +86,7 @@ count = 3!   // triggers
+
+ // 7) Async / Await
+ async function greet_async() => {
+-   sleep(0.1)!
++   sleep 0.1!
+    return "Async greeting complete!"!
+ }!
+ print "Starting async demo..."!
+@@ -152,7 +152,7 @@ synergize {
+
+ // 11) Tiny object pattern via Map
+ function make_point(x, y) => {
+-   const p = Map()!
++   const p = Map!
+    p["x"] = x!
+    p["y"] = y!
+    return p!
+diff --git a/programs/demos/multi_file.gom b/programs/demos/multi_file.gom
+index 7b0146b..13ad115 100644
+--- a/programs/demos/multi_file.gom
++++ b/programs/demos/multi_file.gom
+@@ -27,12 +27,12 @@ const num = 5!
+ print "Number: ${num}"!
+ print ""!
+
+-print "square(${num} = ${square num}")!
+-print "cube(${num} = ${cube num}")!
+-print "double(${num} = ${double num}")!
++print "square(${num} = ${square num})"!
++print "cube(${num} = ${cube num})"!
++print "double(${num} = ${double num})"!
+ print ""!
+
+ print "Pi constant: ${pi}"!
+ const radius = 10!
+ const area = pi * square radius!
+-print "Circle area (r=${radius}: ${area}")!
++print "Circle area (r=${radius}): ${area}"!
+diff --git a/programs/demos/rpg_character.gom b/programs/demos/rpg_character.gom
+index 14f9590..f7e0e40 100644
+--- a/programs/demos/rpg_character.gom
++++ b/programs/demos/rpg_character.gom
+@@ -45,7 +45,7 @@ print ""!
+ hero.takeDamage 30!
+ hero.castSpell 15!
+ hero.heal 20!
+-hero.levelUp()!
++hero.levelUp!
+
+ print ""!
+ print "Final stats:"!
+diff --git a/programs/demos/task_manager.gom b/programs/demos/task_manager.gom
+index ee66167..2443bfe 100644
+--- a/programs/demos/task_manager.gom
++++ b/programs/demos/task_manager.gom
+@@ -32,17 +32,17 @@ task3.name = "Add tests"!
+ task3.priority = 4!
+
+ print "Current tasks:"!
+-task1.info()!
+-task2.info()!
+-task3.info()!
++task1.info!
++task2.info!
++task3.info!
+
+ print ""!
+ print "Completing tasks..."!
+-task2.complete()!
+-task1.complete()!
++task2.complete!
++task1.complete!
+
+ print ""!
+ print "Updated tasks:"!
+-task1.info()!
+-task2.info()!
+-task3.info()!
++task1.info!
++task2.info!
++task3.info!
+diff --git a/programs/examples/00_complete_showcase.gom b/programs/examples/00_complete_showcase.gom
+index 63ed3ff..92c25ae 100644
+--- a/programs/examples/00_complete_showcase.gom
++++ b/programs/examples/00_complete_showcase.gom
+@@ -21,7 +21,7 @@ print "Because programming is 10% skill, 90% luck!"!
+
+ lucky {
+    print "  ✓ Lucky block: Feeling fortunate today!"!
+-   const luckyNumber = Number(7)!
++   const luckyNumber = Number 7!
+    print "    Lucky number:", luckyNumber!
+ }
+
+@@ -51,12 +51,12 @@ whenever {
+ print "\n💼 FEATURE #4: CORPORATE SPEAK"!
+ print "Let's synergize our paradigms!"!
+
+-const innovation = String("Innovation")!
+-const synergy = String("Synergy")!
++const innovation = String "Innovation"!
++const synergy = String "Synergy"!
+ synergize innovation, synergy!
+ print "  ✓ Synergized:", innovation, "with", synergy!
+
+-const impact = Number(100)!
++const impact = Number 100!
+ leverage impact!
+ print "  ✓ Leveraged impact for 2x results!"!
+
+@@ -75,7 +75,7 @@ print "When you know it won't work but try anyway!"!
+
+ unlucky {
+    print "  ✓ This probably won't work..."!
+-   const doom = Number(13)!
++   const doom = Number 13!
+    print "    Doom number:", doom, "(it worked anyway!)"!
+ }
+
+@@ -87,7 +87,7 @@ happy {
+          print "  🎉 Triple combo: Happy + Lucky + Eventually!"!
+          print "  🎉 What are the odds?!"!
+
+-         const magic = String("MAGIC")!
++         const magic = String "MAGIC"!
+          leverage magic!
+          print "  🎉 Leveraged magic:", magic!
+       }
diff --git a/compiler/examples/comprehensive_test.gom b/compiler/examples/comprehensive_test.gom
index 4cfda50..b905f7b 100644
--- a/compiler/examples/comprehensive_test.gom
+++ b/compiler/examples/comprehensive_test.gom
@@ -5,7 +5,7 @@ print "=== GULF OF MEXICO COMPILER - COMPREHENSIVE TEST ==="!

 // Test 1: Map Support
 print "\n1. Map/Dictionary Support"!
-const config = Map()!
+const config = Map !
 print "  Created empty map: OK"!

 // Test 2: Arrays with -1 indexing
diff --git a/compiler/examples/test_maps.gom b/compiler/examples/test_maps.gom
index 2ec0cbc..ffc3599 100644
--- a/compiler/examples/test_maps.gom
+++ b/compiler/examples/test_maps.gom
@@ -2,7 +2,7 @@

 print "=== Testing Map/Dictionary Support ==="!

-const person = Map()!
+const person = Map !
 print "Created empty Map"!

 print "\n=== Testing Array Operations ==="!
diff --git a/examples/mandelbrot.gom b/examples/mandelbrot.gom
index 4c0078d..2fdfe50 100644
--- a/examples/mandelbrot.gom
+++ b/examples/mandelbrot.gom
@@ -9,42 +9,42 @@ const canvas = Canvas 600, 400, "white"!
 print "Canvas initialized - drawing fractal pattern..."!

 // Create color palette from dark blue to white
-const c0 = Color(0, 0, 51)!      // Darkest blue
-const c1 = Color(0, 0, 102)!     // Dark blue
-const c2 = Color(0, 0, 153)!     // Medium dark blue
-const c3 = Color(0, 0, 204)!     // Medium blue
-const c4 = Color(0, 0, 255)!     // Bright blue
-const c5 = Color(51, 51, 255)!   // Purple-blue
-const c6 = Color(102, 102, 255)! // Light purple
-const c7 = Color(153, 153, 255)! // Very light purple
-const c8 = Color(204, 204, 255)! // Almost white
-const c9 = Color(255, 255, 255)! // White
+const c0 = Color 0, 0, 51!      // Darkest blue
+const c1 = Color 0, 0, 102!     // Dark blue
+const c2 = Color 0, 0, 153!     // Medium dark blue
+const c3 = Color 0, 0, 204!     // Medium blue
+const c4 = Color 0, 0, 255!     // Bright blue
+const c5 = Color 51, 51, 255!   // Purple-blue
+const c6 = Color 102, 102, 255! // Light purple
+const c7 = Color 153, 153, 255! // Very light purple
+const c8 = Color 204, 204, 255! // Almost white
+const c9 = Color 255, 255, 255! // White

 print "Drawing gradient background..."!

 // Draw horizontal gradient bands (10 bands of 40 pixels each)
-canvas.pixel(-1, 0, c0)!
-canvas.pixel(-1, 40, c1)!
-canvas.pixel(-1, 80, c2)!
-canvas.pixel(-1, 120, c3)!
-canvas.pixel(-1, 160, c4)!
-canvas.pixel(-1, 200, c5)!
-canvas.pixel(-1, 240, c6)!
-canvas.pixel(-1, 280, c7)!
-canvas.pixel(-1, 320, c8)!
-canvas.pixel(-1, 360, c9)!
+canvas.pixel -1, 0, c0!
+canvas.pixel -1, 40, c1!
+canvas.pixel -1, 80, c2!
+canvas.pixel -1, 120, c3!
+canvas.pixel -1, 160, c4!
+canvas.pixel -1, 200, c5!
+canvas.pixel -1, 240, c6!
+canvas.pixel -1, 280, c7!
+canvas.pixel -1, 320, c8!
+canvas.pixel -1, 360, c9!

 print "Drawing central fractal bulb..."!

 // Draw some pixels to create a simple pattern
-canvas.pixel(299, 199, c9)!
-canvas.pixel(300, 200, c8)!
-canvas.pixel(298, 198, c7)!
+canvas.pixel 299, 199, c9!
+canvas.pixel 300, 200, c8!
+canvas.pixel 298, 198, c7!

 print "Finalizing fractal image..."!

 // Save the fractal image
-canvas.save("mandelbrot.png")!
+canvas.save "mandelbrot.png"!

 print ""!
 print "===================================="!
diff --git a/gulfofmexico/ide/app.py b/gulfofmexico/ide/app.py
index 6e0cdb4..2f89395 100644
--- a/gulfofmexico/ide/app.py
+++ b/gulfofmexico/ide/app.py
@@ -2,13 +2,15 @@ from __future__ import annotations

 import json
 import os
+import socket
 from functools import partial
+from html import escape as _html_escape
 from pathlib import Path

 # Use compatibility layer for Qt
 try:
     from gulfofmexico.ide.qt_compat import (
-        QT_VERSION,
+        # QT_VERSION,
         QAction,
         QApplication,
         QDockWidget,
@@ -37,6 +39,26 @@ except ImportError as e:
     print("Install with: pip install PySide6 or pip install PyQt5")

 from gulfofmexico.ide.runner import ExecutionSession, run_code
+from gulfofmexico.ide.web_ide import run_web_ide
+
+
+def _format_error_html(err: str) -> str:
+    """Return HTML-safe formatted error snippet for console display.
+
+    Uses monospace <pre> with the GOM error color so rich text appears correctly in
+    the Qt console without allowing raw HTML injection.
+    """
+    return f"<pre style='color:#e06c75; font-family:monospace; white-space: pre-wrap;'>{_html_escape(err)}</pre>"
+
+
+def is_port_open(port: int) -> bool:
+    """Return True if a TCP server is accepting connections on localhost:port."""
+    try:
+        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
+            return True
+    except OSError:
+        return False
+

 if PYSIDE_AVAILABLE:
     # Local imports only when GUI libs are present
@@ -271,9 +293,9 @@ if PYSIDE_AVAILABLE:
             if out:
                 self.console.append(out)
             if err:
-                prefix = "<span style='color:# e06c75'>"
-                suffix = "</span>"
-                self.console.append(prefix + err + suffix)
+                # format and escape error output to avoid raw HTML + use readable monospace
+                html_err = _format_error_html(err)
+                self.console.append(html_err)
             self.btn_run.setEnabled(True)
             self.btn_stop.setEnabled(False)
             self.statusBar().showMessage("Ready")
@@ -350,6 +372,13 @@ if PYSIDE_AVAILABLE:
             act_clear.triggered.connect(self._clear_console)
             run_menu.addAction(act_clear)

+            # Tools menu - allow launching the web IDE from the Qt app
+            tools_menu = mb.addMenu("Tools")
+            act_open_webide = QAction("Open Web IDE", self)
+            act_open_webide.setShortcut("Ctrl+Shift+W")
+            act_open_webide.triggered.connect(self._open_web_ide)
+            tools_menu.addAction(act_open_webide)
+
         def _maybe_save_editor(self, ed: "CodeEditor") -> bool:
             if not ed.document().isModified():
                 return True
@@ -382,6 +411,42 @@ if PYSIDE_AVAILABLE:
         def _clear_console(self) -> None:
             self.console.clear()

+        def _open_web_ide(self, port: int | None = None) -> None:
+            """Start or open the Web IDE in the user's browser.
+
+            Behavior:
+            - If a server is already running on the preferred port (default 8080), open it.
+            - Otherwise start the bundled web IDE in a background thread.
+            """
+            import threading
+            import webbrowser
+
+            preferred = port or 8080
+
+            def _port_open(p: int) -> bool:
+                try:
+                    with socket.create_connection(("127.0.0.1", p), timeout=0.3):
+                        return True
+                except OSError:
+                    return False
+
+            if _port_open(preferred):
+                url = f"http://localhost:{preferred}/ide"
+                webbrowser.open(url)
+                self.statusBar().showMessage(f"Opened existing Web IDE at {url}")
+                return
+
+            # Try to start the web IDE server in a background thread
+            def _start_server():
+                try:
+                    run_web_ide(preferred)
+                except OSError:  # port in use or failed to bind
+                    # If run_web_ide fails (port taken), open the browser in case it's an external server
+                    webbrowser.open(f"http://localhost:{preferred}/ide")
+
+            threading.Thread(target=_start_server, daemon=True).start()
+            self.statusBar().showMessage(f"Starting Web IDE on port {preferred} — opening browser")
+
         def _show_console_menu(self, pos) -> None:
             menu = QMenu(self)
             act_copy = QAction("Copy All", self)
diff --git a/programs/01_basics/03_arrays.gom b/programs/01_basics/03_arrays.gom
index 581c602..fe99798 100644
--- a/programs/01_basics/03_arrays.gom
+++ b/programs/01_basics/03_arrays.gom
@@ -2,10 +2,10 @@

 const numbers = [10, 20, 30, 40, 50]!

-print "First element (index -1: ${numbers[-1]}")!
-print "Second element (index 0: ${numbers[0]}")!
-print "Third element (index 1: ${numbers[1]}")!
-print "Last element (index 3: ${numbers[3]}")!
+print "First element (index -1): ${numbers[-1]}"!
+print "Second element (index 0): ${numbers[0]}"!
+print "Third element (index 1): ${numbers[1]}"!
+print "Last element (index 3): ${numbers[3]}"!

 // Fractional indexing
 const colors = ["red", "blue"]!
diff --git a/programs/01_basics/04_probabilistic.gom b/programs/01_basics/04_probabilistic.gom
index e348c48..449772a 100644
--- a/programs/01_basics/04_probabilistic.gom
+++ b/programs/01_basics/04_probabilistic.gom
@@ -7,7 +7,7 @@ var value = 20!!
 print "Value with confidence 2: ${value}"!

 var value = 5!!!
-print "Value with confidence 3 (wins!: ${value}")!
+print "Value with confidence 3 (wins!): ${value}"!

 var value = 100!!!!
-print "Value with confidence 4 (highest!: ${value}")!
+print "Value with confidence 4 (highest!): ${value}"!
diff --git a/programs/01_basics/06_classes.gom b/programs/01_basics/06_classes.gom
index f6d3336..b3dba8e 100644
--- a/programs/01_basics/06_classes.gom
+++ b/programs/01_basics/06_classes.gom
@@ -18,10 +18,10 @@ class Person {
 const alice = new Person!
 alice.name = "Alice"!
 alice.age = 25!
-alice.introduce()!
+alice.introduce !

 const bob = new Person!
 bob.name = "Bob"!
 bob.age = 30!
-bob.introduce()!
-bob.birthday()!
+bob.introduce !
+bob.birthday !
diff --git a/programs/02_features/12_async.gom b/programs/02_features/12_async.gom
index 4b1c0bb..d854c5e 100644
--- a/programs/02_features/12_async.gom
+++ b/programs/02_features/12_async.gom
@@ -11,8 +11,8 @@ async function processData(value) => {
 }!

 // Call async functions
-const result = await fetchData()!
+const result = await fetchData!
 print "Fetched result: ${result}"!

-const processed = await processData(result)!
+const processed = await processData result!
 print "Processed result: ${processed}"!
diff --git a/programs/02_features/14_arithmetic.gom b/programs/02_features/14_arithmetic.gom
index 8c937f3..507738e 100644
--- a/programs/02_features/14_arithmetic.gom
+++ b/programs/02_features/14_arithmetic.gom
@@ -11,4 +11,4 @@ print "Power: ${a} ^ ${b} = ${a ^ b}"!

 // Complex expressions
 const result = (a + b) * 2 ^ 3!
-print "(${a} + ${b} * 2 ^ 3 = ${result}")!
+print "(${a} + ${b} * 2 ^ 3 = ${result})"!
diff --git a/programs/03_graphics/18_generative_art.gom b/programs/03_graphics/18_generative_art.gom
index 110a71f..d7fe2bf 100644
--- a/programs/03_graphics/18_generative_art.gom
+++ b/programs/03_graphics/18_generative_art.gom
@@ -17,7 +17,7 @@ function fn drawCircleGrid() {
       var otherColor "blue"!!!

       // Use maybe to randomly choose properties
-      const useOther = Boolean(maybe)!
+      const useOther = Boolean maybe!
       const finalColor = useOther ? otherColor : circleColor!

       // Position with -1 based indexing
@@ -27,29 +27,29 @@ function fn drawCircleGrid() {
       // Radius with some randomness
       var baseRadius 15!!
       var bigRadius 20!!!
-      const radius = Boolean(maybe) ? bigRadius : baseRadius!
+      const radius = Boolean maybe ? bigRadius : baseRadius!

-      canvas.circle(x, y, radius, finalColor)!
+      canvas.circle x, y, radius, finalColor!

       var col col + 1!
    }

    // Draw 15 circles in this row
    drawRow!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
-   drawRow()!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!
+   drawRow!

    var row row + 1!
 }
diff --git a/programs/03_graphics/19_mandelbrot.gom b/programs/03_graphics/19_mandelbrot.gom
index a742d6d..88a10ad 100644
--- a/programs/03_graphics/19_mandelbrot.gom
+++ b/programs/03_graphics/19_mandelbrot.gom
@@ -3,7 +3,7 @@ print "Starting Mandelbrot generation..."!

 const width = 100!
 const height = 100!
-const canvas = Canvas(width, height, "black")!
+const canvas = Canvas width, height, "black"!

 print "Canvas created"!

@@ -23,7 +23,7 @@ var col = -1!
 // Draw a simple gradient as a test
 function drawPixel(x, y, iter) => {
    const color = iter == 0 ? c0 : (iter == 1 ? c1 : (iter == 2 ? c2 : c3))!
-   canvas.pixel(x, y, color)!
+   canvas.pixel x, y, color!
 }!

 // Process one pixel
@@ -35,7 +35,7 @@ function processPixel() => {
    // Simple iteration count (just based on position for now)
    const iter = ((col + row) % 4)!

-   drawPixel(col, row, iter)!
+   drawPixel col, row, iter!

    col = col + 1!
 }!
@@ -44,35 +44,35 @@ function processPixel() => {
 function processRow() => {
    col = -1!

-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
-   processPixel()!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!
+   processPixel!

    row = row + 1!
 }!

 print "Starting to draw..."!

-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
-processRow()!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!
+processRow!

 print "Drawing complete!"!

-canvas.save("mandelbrot.png")!
+canvas.save "mandelbrot.png"!

 print "Mandelbrot set saved to mandelbrot.png"!
diff --git a/programs/03_graphics/mandelbrot_simple.gom b/programs/03_graphics/mandelbrot_simple.gom
index d6d6d51..9d9586d 100644
--- a/programs/03_graphics/mandelbrot_simple.gom
+++ b/programs/03_graphics/mandelbrot_simple.gom
@@ -3,15 +3,15 @@

 print "Creating fractal art..."!

-const canvas = Canvas(400, 300, "black")!
+const canvas = Canvas 400, 300, "black"!

 // Color palette - blues to whites
-const c0 = Color(0, 0, 51)!     // Dark blue
-const c1 = Color(0, 0, 102)!    // Medium blue
-const c2 = Color(51, 102, 204)! // Bright blue
-const c3 = Color(102, 153, 255)! // Light blue
-const c4 = Color(204, 229, 255)! // Very light blue
-const c5 = Color(255, 255, 255)! // White
+const c0 = Color 0, 0, 51!     // Dark blue
+const c1 = Color 0, 0, 102!    // Medium blue
+const c2 = Color 51, 102, 204! // Bright blue
+const c3 = Color 102, 153, 255! // Light blue
+const c4 = Color 204, 229, 255! // Very light blue
+const c5 = Color 255, 255, 255! // White

 print "Colors created"!

diff --git a/programs/04_satirical/19_passive_aggressive_errors.gom b/programs/04_satirical/19_passive_aggressive_errors.gom
index 6972155..c005fda 100644
--- a/programs/04_satirical/19_passive_aggressive_errors.gom
+++ b/programs/04_satirical/19_passive_aggressive_errors.gom
@@ -5,7 +5,7 @@ print "=== Passive-Aggressive Error Handling ==="!

 // Example 1: Division by zero (whatever!)
 try {
-   const result = Number(10) / Number(0)!
+   const result = Number(10) / Number 0!
    print "Result:", result!
 } whatever {
    print "Math is hard, let's go shopping"!
@@ -20,7 +20,7 @@ try {

 // Example 3: Invalid operation (whatever!)
 try {
-   const broken = String("hello") - Number(5)!
+   const broken = String("hello") - Number 5!
    print broken!
 } whatever {
    print "Whatever, I didn't want to do that anyway"!
@@ -28,7 +28,7 @@ try {

 // Example 4: Actually successful code
 try {
-   const x = Number(42)!
+   const x = Number 42!
    print "Success! x =", x!
 } whatever {
    print "This shouldn't print"!
diff --git a/programs/04_satirical/21_corporate_speak.gom b/programs/04_satirical/21_corporate_speak.gom
index 7e1888d..cbd4d63 100644
--- a/programs/04_satirical/21_corporate_speak.gom
+++ b/programs/04_satirical/21_corporate_speak.gom
@@ -5,37 +5,37 @@ print "=== Corporate Synergy Meeting ==="!

 // synergize: Combine two values
 print "\n1. SYNERGIZE (combining values):"!
-const name1 = String("Innovative")!
-const name2 = String("Solutions")!
+const name1 = String "Innovative"!
+const name2 = String "Solutions"!
 synergize name1, name2!
 print "  Company name:", name1, "+", name2!

-const revenue = Number(100000)!
-const profit = Number(50000)!
+const revenue = Number 100000!
+const profit = Number 50000!
 synergize revenue, profit!
 print "  Total:", revenue, "+", profit!

 // leverage: Multiply by 2 (for maximum impact!)
 print "\n2. LEVERAGE (doubling for impact):"!
-const sales = Number(1000)!
+const sales = Number 1000!
 leverage sales!
 print "  Leveraged sales: 1000 * 2"!

-const buzz = String("Synergy")!
+const buzz = String "Synergy"!
 leverage buzz!
 print "  Leveraged buzzword: Synergy * 2"!

 // paradigm_shift: Negate or reverse
 print "\n3. PARADIGM SHIFT (complete reversal):"!
-const oldThinking = Number(100)!
+const oldThinking = Number 100!
 paradigm_shift oldThinking!
 print "  Old thinking: 100 -> -100"!

-const direction = String("forward")!
+const direction = String "forward"!
 paradigm_shift direction!
 print "  Direction: forward -> backward"!

-const mindset = Boolean(true)!
+const mindset = Boolean true!
 paradigm_shift mindset!
 print "  Mindset: true -> false"!

diff --git a/programs/04_satirical/22_satirical_showcase.gom b/programs/04_satirical/22_satirical_showcase.gom
index 4549a60..2414a4f 100644
--- a/programs/04_satirical/22_satirical_showcase.gom
+++ b/programs/04_satirical/22_satirical_showcase.gom
@@ -7,8 +7,8 @@ print "=== The Ultimate Corporate Procrastinator ==="!
 try {
    print "\n🏢 QUARTERLY PLANNING SESSION"!

-   const q1_target = Number(1000000)!
-   const q1_actual = Number(750000)!
+   const q1_target = Number 1000000!
+   const q1_actual = Number 750000!

    synergize q1_target, q1_actual!
    leverage q1_actual!
@@ -26,7 +26,7 @@ later {
    print "  • Update TPS reports"!

    try {
-      const reports = Number(47)!
+      const reports = Number 47!
       leverage reports!
       print "    Leveraged those reports to", reports!
    } whatever {
@@ -48,13 +48,13 @@ whenever {
 print "\n💼 STRATEGIC INITIATIVES:"!

 try {
-   const oldStrategy = String("reactive")!
+   const oldStrategy = String "reactive"!
    paradigm_shift oldStrategy!
    print "Shifted from reactive to proactive approach"!

    later {
-      const synergy = String("cross-functional")!
-      const alignment = String("stakeholder")!
+      const synergy = String "cross-functional"!
+      const alignment = String "stakeholder"!
       synergize synergy, alignment!
       print "Creating", synergy, alignment, "synergies"!
    }
diff --git a/programs/04_satirical/24_superstitious_programming.gom b/programs/04_satirical/24_superstitious_programming.gom
index f84da72..873c2a8 100644
--- a/programs/04_satirical/24_superstitious_programming.gom
+++ b/programs/04_satirical/24_superstitious_programming.gom
@@ -6,7 +6,7 @@ print "=== Superstitious Programming Demo ==="!
 // Lucky block - good fortune expected
 lucky {
    print "Attempting risky operation..."!
-   const result = Number(42) / Number(2)!
+   const result = Number(42) / Number 2!
    print "Result:", result!
 }

@@ -14,7 +14,7 @@ lucky {
 print "\nCrossing fingers for success..."!
 cross_fingers {
    print "This might work, this might not!"!
-   const magic = Number(777)!
+   const magic = Number 777!
    print "Magic number:", magic!
 }

@@ -27,14 +27,14 @@ cross_fingers {
 print "\nKnocking on wood for protection..."!
 knock_on_wood {
    print "This is protected by superstition!"!
-   const safe = String("safe and sound")!
+   const safe = String "safe and sound"!
    print safe!
 }

 // Unlucky block - expect failure
 unlucky {
    print "This probably won't work..."!
-   const doom = Number(13)!
+   const doom = Number 13!
    print "Doom number:", doom!
 }

diff --git a/programs/04_satirical/25_ultimate_satire.gom b/programs/04_satirical/25_ultimate_satire.gom
index 89d2ca0..3531e69 100644
--- a/programs/04_satirical/25_ultimate_satire.gom
+++ b/programs/04_satirical/25_ultimate_satire.gom
@@ -8,8 +8,8 @@ happy {
    print "\n😊 Beginning with positive vibes!"!

    // Corporate speak in happy mode
-   const team = String("A-Team")!
-   const project = String("MVP")!
+   const team = String "A-Team"!
+   const project = String "MVP"!
    synergize team, project!
    print "Synergized:", team, "with", project!
 }
@@ -17,7 +17,7 @@ happy {
 // Excited about the possibilities
 excited {
    print "\n🎉 Super excited to leverage our synergies!"!
-   leverage String("HYPE")!
+   leverage String "HYPE"!
 }

 // Procrastinate on important stuff
@@ -39,7 +39,7 @@ lucky {
       knock_on_wood {
          print "Triple protection: Lucky + Crossed Fingers + Knocked Wood!"!
          print "Deploying..."!
-         const deploy = String("SUCCESS")!
+         const deploy = String "SUCCESS"!
          print "Status:", deploy!
       }
    }
@@ -52,7 +52,7 @@ tired {
 }

 // Paradigm shift the thinking
-const oldWay = String("waterfall")!
+const oldWay = String "waterfall"!
 print "\nOld methodology:", oldWay!
 paradigm_shift oldWay!
 print "New methodology: paradigm shifted!"!
diff --git a/programs/04_satirical/26_quantum_programming.gom b/programs/04_satirical/26_quantum_programming.gom
index 68a3df9..9a0259f 100644
--- a/programs/04_satirical/26_quantum_programming.gom
+++ b/programs/04_satirical/26_quantum_programming.gom
@@ -15,7 +15,7 @@ print "   Until we observe it, it's both 1 AND 2 AND 3 AND 4 AND 5!"!

 print ""!
 print "3. Observing quantum variable (collapses wavefunction)..."!
-const result = observe("x")!
+const result = observe "x"!
 print "   Result: ${result}"!

 print ""!
@@ -31,9 +31,9 @@ quantum c ["cat", "dog", "bird"]!

 print ""!
 print "6. Observing all quantum states..."!
-const val_a = observe("a")!
-const val_b = observe("b")!
-const val_c = observe("c")!
+const val_a = observe "a"!
+const val_b = observe "b"!
+const val_c = observe "c"!

 print "   a collapsed to: ${val_a}"!
 print "   b collapsed to: ${val_b}"!
diff --git a/programs/04_satirical/27_time_travel.gom b/programs/04_satirical/27_time_travel.gom
index 6e793ac..523acc2 100644
--- a/programs/04_satirical/27_time_travel.gom
+++ b/programs/04_satirical/27_time_travel.gom
@@ -20,9 +20,9 @@ print "3. Current value of counter: ${counter}"!

 print ""!
 print "4. Accessing PAST values..."!
-const past_1 = past("counter", 1)!
-const past_3 = past("counter", 3)!
-const past_5 = past("counter", 5)!
+const past_1 = past "counter", 1!
+const past_3 = past "counter", 3!
+const past_5 = past "counter", 5!

 print "   1 step ago: ${past_1}"!
 print "   3 steps ago: ${past_3}"!
@@ -30,14 +30,14 @@ print "   5 steps ago: ${past_5}"!

 print ""!
 print "5. Predicting the FUTURE..."!
-const future_val = future("counter")!
+const future_val = future "counter"!
 print "   Future prediction: ${future_val}"!
 print "   (Disclaimer: The future is unknowable and random!)"!

 print ""!
 print "6. Creating a timeline paradox..."!
 var x 100!
-const past_x = past("x", 1)!
+const past_x = past "x", 1!
 print "   Past value that doesn't exist: ${past_x}"!
 print "   (Returns 0 for non-existent history)"!

@@ -48,10 +48,10 @@ temperature = 22!
 temperature = 25!
 temperature = 30!

-const yesterday_temp = past("temperature", 2)!
+const yesterday_temp = past "temperature", 2!
 print "   Temperature 2 steps ago: ${yesterday_temp}°C"!

-const predicted_temp = future("temperature")!
+const predicted_temp = future "temperature"!
 print "   Predicted future temperature: ${predicted_temp}°C"!

 print ""!
diff --git a/programs/04_satirical/28_quantum_time_spectacular.gom b/programs/04_satirical/28_quantum_time_spectacular.gom
index a3a374f..5adb087 100644
--- a/programs/04_satirical/28_quantum_time_spectacular.gom
+++ b/programs/04_satirical/28_quantum_time_spectacular.gom
@@ -8,20 +8,20 @@ print ""!
 print "Part 1: Quantum Time Travel Paradox"!
 print "------------------------------------"!
 quantum timeline [1, 2, 3, 4, 5]!
-const collapsed_timeline = observe("timeline")!
+const collapsed_timeline = observe "timeline"!
 print "Timeline collapsed to: ${collapsed_timeline}"!

-const past_timeline = past("collapsed_timeline", 1)!
+const past_timeline = past "collapsed_timeline", 1!
 print "But in the past, timeline was: ${past_timeline}"!

 print ""!
 print "Part 2: Superposition of Futures"!
 print "---------------------------------"!
 quantum future_paths ["success", "failure", "maybe"]!
-const chosen_path = observe("future_paths")!
+const chosen_path = observe "future_paths"!
 print "The universe chose: ${chosen_path}"!

-const predicted = future("chosen_path")!
+const predicted = future "chosen_path"!
 print "But the future predicts: ${predicted}"!

 print ""!
@@ -30,7 +30,7 @@ print "---------------------------------"!

 happy {
    quantum mood ["joyful", "ecstatic", "content"]!
-   const current_mood = observe("mood")!
+   const current_mood = observe "mood"!
    print "😊 In a happy state, mood is: ${current_mood}"!
 }

@@ -40,7 +40,7 @@ print "-------------------------------"!

 lucky {
    quantum lottery [7, 13, 42, 99]!
-   const winning_number = observe("lottery")!
+   const winning_number = observe "lottery"!
    print "🍀 Your lucky number is: ${winning_number}!"!
 }

@@ -54,7 +54,7 @@ emotion = "excited"!
 emotion = "tired"!

 excited {
-   const past_emotion = past("emotion", 2)!
+   const past_emotion = past "emotion", 2!
    print "🎉 Two emotional states ago, we were: ${past_emotion}!"!
 }

@@ -64,10 +64,10 @@ print "-----------------------------"!

 quantum reality ["real", "simulation", "dream", "maybe"]!
 cross_fingers {
-   const our_reality = observe("reality")!
+   const our_reality = observe "reality"!
    print "🤞 We live in: ${our_reality}"!

-   const future_reality = future("our_reality")!
+   const future_reality = future "our_reality"!
    print "🔮 Future reality prediction: ${future_reality}"!
 }

diff --git a/programs/05_analysis/36_base_numbers.gom b/programs/05_analysis/36_base_numbers.gom
index 07bb624..20fed22 100644
--- a/programs/05_analysis/36_base_numbers.gom
+++ b/programs/05_analysis/36_base_numbers.gom
@@ -10,31 +10,31 @@ print "------------------------------"!
 const decimal = 42!
 print "Decimal: ${decimal}"!

-const binary = to_binary(decimal)!
+const binary = to_binary decimal!
 print "Binary (base 2): ${binary}"!

-const octal = to_octal(decimal)!
+const octal = to_octal decimal!
 print "Octal (base 8): ${octal}"!

-const hex = to_hex(decimal)!
+const hex = to_hex decimal!
 print "Hexadecimal (base 16): ${hex}"!

-const base5 = to_base(decimal, 5)!
+const base5 = to_base decimal, 5!
 print "Base 5: ${base5}"!

 print ""!
 print "Part 2: Converting Back to Decimal"!
 print "-----------------------------------"!
-const from_bin = from_binary("101010")!
+const from_bin = from_binary "101010"!
 print "Binary '101010' to decimal: ${from_bin}"!

-const from_oct = from_octal("52")!
+const from_oct = from_octal "52"!
 print "Octal '52' to decimal: ${from_oct}"!

-const from_h = from_hex("2A")!
+const from_h = from_hex "2A"!
 print "Hex '2A' to decimal: ${from_h}"!

-const from_b5 = from_base("132", 5)!
+const from_b5 = from_base "132", 5!
 print "Base 5 '132' to decimal: ${from_b5}"!

 print ""!
@@ -43,16 +43,16 @@ print "-----------------------------------"!
 const num = 255!
 print "Converting ${num} to different bases:"!

-const base3 = to_base(num, 3)!
+const base3 = to_base num, 3!
 print "  Base 3: ${base3}"!

-const base7 = to_base(num, 7)!
+const base7 = to_base num, 7!
 print "  Base 7: ${base7}"!

-const base12 = to_base(num, 12)!
+const base12 = to_base num, 12!
 print "  Base 12: ${base12}"!

-const base36 = to_base(num, 36)!
+const base36 = to_base num, 36!
 print "  Base 36: ${base36}"!

 print ""!
@@ -61,28 +61,28 @@ print "------------------------------"!
 print "Adding binary and hex, result in octal:"!
 const bin_num = "1010"!  // 10 in decimal
 const hex_num = "14"!    // 20 in decimal
-const sum_oct = base_add(bin_num, 2, hex_num, 16, 8)!
+const sum_oct = base_add bin_num, 2, hex_num, 16, 8!
 print "  Binary ${bin_num} + Hex ${hex_num} = Octal ${sum_oct}"!

 print ""!
 print "Subtracting in different bases:"!
 const oct_a = "100"!  // 64 in decimal
 const dec_b = 14!
-const diff_bin = base_sub(oct_a, 8, dec_b, 10, 2)!
+const diff_bin = base_sub oct_a, 8, dec_b, 10, 2!
 print "  Octal ${oct_a} - Decimal ${dec_b} = Binary ${diff_bin}"!

 print ""!
 print "Multiplying across bases:"!
 const base5_x = "23"!  // 13 in decimal
 const base7_y = "12"!  // 9 in decimal
-const product_hex = base_mul(base5_x, 5, base7_y, 7, 16)!
+const product_hex = base_mul base5_x, 5, base7_y, 7, 16!
 print "  Base5 ${base5_x} * Base7 ${base7_y} = Hex ${product_hex}"!

 print ""!
 print "Division with different bases:"!
 const hex_dividend = "64"!  // 100 in decimal
 const bin_divisor = "101"!  // 5 in decimal
-const quotient_oct = base_div(hex_dividend, 16, bin_divisor, 2, 8)!
+const quotient_oct = base_div hex_dividend, 16, bin_divisor, 2, 8!
 print "  Hex ${hex_dividend} / Binary ${bin_divisor} = Octal ${quotient_oct}"!

 print ""!
@@ -91,13 +91,13 @@ print "----------------------------------"!
 print "Calculate Fibonacci in base 7:"!
 var a = 0!
 var b = 1!
-print "F(0) = ${to_base(a, 7)}"!
-print "F(1) = ${to_base(b, 7)}"!
+print "F(0) = ${to_base a, 7}"!
+print "F(1) = ${to_base b, 7}"!

 var i = 2!
 when i < 10 {
    const next = a + b!
-   print "F(${i}) = ${to_base(next, 7)}"!
+   print "F(${i}) = ${to_base next, 7}"!
    a = b!
    b = next!
    i = i + 1!
@@ -111,10 +111,10 @@ print "-------|------|-----|-----|-----|----"!

 var n = 0!
 when n < 17 {
-   const b2 = to_binary(n)!
-   const b8 = to_octal(n)!
-   const b16 = to_hex(n)!
-   const b36 = to_base(n, 36)!
+   const b2 = to_binary n!
+   const b8 = to_octal n!
+   const b16 = to_hex n!
+   const b36 = to_base n, 36!
    print "${n}      | ${b2}  | ${b8}   | ${n}   | ${b16}   | ${b36}"!
    n = n + 1!
 }!
diff --git a/programs/05_analysis/37_base_simple.gom b/programs/05_analysis/37_base_simple.gom
index d7c8f3a..cc75808 100644
--- a/programs/05_analysis/37_base_simple.gom
+++ b/programs/05_analysis/37_base_simple.gom
@@ -6,10 +6,10 @@ print ""!

 // Test basic conversions
 print "Convert 42 to different bases:"!
-print "Binary: ${to_binary(42)}"!
-print "Octal: ${to_octal(42)}"!
-print "Hex: ${to_hex(42)}"!
-print "Base 5: ${to_base(42, 5)}"!
+print "Binary: ${to_binary 42}"!
+print "Octal: ${to_octal 42}"!
+print "Hex: ${to_hex 42}"!
+print "Base 5: ${to_base 42, 5}"!
 print ""!

 // Test conversions back to decimal
@@ -18,34 +18,34 @@ const bin_str = "101010"!
 const oct_str = "52"!
 const hex_str = "2A"!
 const b5_str = "132"!
-print "Binary 101010 = ${from_binary(bin_str)}"!
-print "Octal 52 = ${from_octal(oct_str)}"!
-print "Hex 2A = ${from_hex(hex_str)}"!
-print "Base 5 '132' = ${from_base(b5_str, 5)}"!
+print "Binary 101010 = ${from_binary bin_str}"!
+print "Octal 52 = ${from_octal oct_str}"!
+print "Hex 2A = ${from_hex hex_str}"!
+print "Base 5 '132' = ${from_base b5_str, 5}"!
 print ""!

 // Test cross-base arithmetic
 print "Cross-base arithmetic:"!
-const add_result = base_add("1010", 2, "14", 16, 8)!
+const add_result = base_add "1010", 2, "14", 16, 8!
 print "Binary 1010 + Hex 14 (in octal) = ${add_result}"!
-const sub_result = base_sub("100", 8, 14, 10, 2)!
+const sub_result = base_sub "100", 8, 14, 10, 2!
 print "Octal 100 - Decimal 14 (in binary) = ${sub_result}"!
-const mul_result = base_mul("23", 5, "12", 7, 16)!
+const mul_result = base_mul "23", 5, "12", 7, 16!
 print "Base5 23 * Base7 12 (in hex) = ${mul_result}"!
-const div_result = base_div("64", 16, "101", 2, 8)!
+const div_result = base_div "64", 16, "101", 2, 8!
 print "Hex 64 / Binary 101 (in octal) = ${div_result}"!
 print ""!

 // Test edge cases
 print "Edge cases:"!
-const zero_b2 = to_base(0, 2)!
+const zero_b2 = to_base 0, 2!
 print "Zero in base 2: ${zero_b2}"!
-const zero_b36 = to_base(0, 36)!
+const zero_b36 = to_base 0, 36!
 print "Zero in base 36: ${zero_b36}"!
-const n255_b36 = to_base(255, 36)!
+const n255_b36 = to_base 255, 36!
 print "255 in base 36: ${n255_b36}"!
 const zz_str = "ZZ"!
-const zz_dec = from_base(zz_str, 36)!
+const zz_dec = from_base zz_str, 36!
 print "Base 36 'ZZ' to decimal: ${zz_dec}"!
 print ""!

diff --git a/programs/05_analysis/38_base_practical.gom b/programs/05_analysis/38_base_practical.gom
index 3f0ea71..3190d65 100644
--- a/programs/05_analysis/38_base_practical.gom
+++ b/programs/05_analysis/38_base_practical.gom
@@ -13,10 +13,10 @@ const ip_oct2 = 168!
 const ip_oct3 = 1!
 const ip_oct4 = 254!

-const bin1 = to_binary(ip_oct1)!
-const bin2 = to_binary(ip_oct2)!
-const bin3 = to_binary(ip_oct3)!
-const bin4 = to_binary(ip_oct4)!
+const bin1 = to_binary ip_oct1!
+const bin2 = to_binary ip_oct2!
+const bin3 = to_binary ip_oct3!
+const bin4 = to_binary ip_oct4!

 print "IP Address: ${ip_oct1}.${ip_oct2}.${ip_oct3}.${ip_oct4}"!
 print "Binary: ${bin1}.${bin2}.${bin3}.${bin4}"!
@@ -29,9 +29,9 @@ const red = 255!
 const green = 99!
 const blue = 71!

-const hex_r = to_hex(red)!
-const hex_g = to_hex(green)!
-const hex_b = to_hex(blue)!
+const hex_r = to_hex red!
+const hex_g = to_hex green!
+const hex_b = to_hex blue!

 print "RGB: (${red}, ${green}, ${blue})"!
 print "Hex color: #${hex_r}${hex_g}${hex_b}"!
@@ -44,8 +44,8 @@ const owner_rwx = 7!  // read=4, write=2, execute=1
 const group_rx = 5!   // read=4, execute=1
 const other_r = 4!    // read=4

-const perm_oct = to_octal(owner_rwx * 64 + group_rx * 8 + other_r)!
-const perm_bin = to_binary(owner_rwx * 64 + group_rx * 8 + other_r)!
+const perm_oct = to_octal owner_rwx * 64 + group_rx * 8 + other_r!
+const perm_bin = to_binary owner_rwx * 64 + group_rx * 8 + other_r!

 print "Permissions: ${owner_rwx}${group_rx}${other_r} (octal)"!
 print "Full octal: ${perm_oct}"!
@@ -57,8 +57,8 @@ print ""!
 print "4. Memory Address Conversion"!
 print "-----------------------------"!
 const mem_addr = 65535!
-const mem_hex = to_hex(mem_addr)!
-const mem_bin = to_binary(mem_addr)!
+const mem_hex = to_hex mem_addr!
+const mem_bin = to_binary mem_addr!

 print "Decimal address: ${mem_addr}"!
 print "Hex: 0x${mem_hex}"!
@@ -69,10 +69,10 @@ print ""!
 print "5. Custom Base Encoding"!
 print "-----------------------"!
 const data = 12345!
-const base32 = to_base(data, 32)!
+const base32 = to_base data, 32!
 print "Data: ${data}"!
 print "Base-32 encoded: ${base32}"!
-const decoded = from_base(base32, 32)!
+const decoded = from_base base32, 32!
 print "Decoded back: ${decoded}"!
 print ""!

@@ -82,9 +82,9 @@ print "--------------"!
 const bin_a = "1111"!  // 15 in decimal
 const bin_b = "1010"!  // 10 in decimal

-const sum_bin = base_add(bin_a, 2, bin_b, 2, 2)!
-const diff_bin = base_sub(bin_a, 2, bin_b, 2, 2)!
-const prod_bin = base_mul(bin_a, 2, bin_b, 2, 2)!
+const sum_bin = base_add bin_a, 2, bin_b, 2, 2!
+const diff_bin = base_sub bin_a, 2, bin_b, 2, 2!
+const prod_bin = base_mul bin_a, 2, bin_b, 2, 2!

 print "Binary ${bin_a} + ${bin_b} = ${sum_bin}"!
 print "Binary ${bin_a} - ${bin_b} = ${diff_bin}"!
@@ -96,8 +96,8 @@ print "7. Check Powers of 2"!
 print "--------------------"!
 const num16 = 16!
 const num20 = 20!
-const bin16 = to_binary(num16)!
-const bin20 = to_binary(num20)!
+const bin16 = to_binary num16!
+const bin20 = to_binary num20!

 print "${num16} in binary: ${bin16} (power of 2!)"!
 print "${num20} in binary: ${bin20} (not power of 2)"!
diff --git a/programs/05_analysis/39_statistics.gom b/programs/05_analysis/39_statistics.gom
index fcb9ecc..60561c8 100644
--- a/programs/05_analysis/39_statistics.gom
+++ b/programs/05_analysis/39_statistics.gom
@@ -14,29 +14,29 @@ print ""!
 // Basic statistics
 print "1. Measures of Central Tendency"!
 print "--------------------------------"!
-const avg = mean(scores)!
+const avg = mean scores!
 print "Mean (Average): ${avg}"!

-const mid = median(scores)!
+const mid = median scores!
 print "Median (Middle): ${mid}"!

-const most_common = mode(scores)!
+const most_common = mode scores!
 print "Mode (Most frequent): ${most_common}"!
 print ""!

 // Measures of spread
 print "2. Measures of Variability"!
 print "---------------------------"!
-const var = variance(scores)!
+const var = variance scores!
 print "Variance: ${var}"!

-const sd = stdev(scores)!
+const sd = stdev scores!
 print "Standard Deviation: ${sd}"!

-const min_score = min_val(scores)!
+const min_score = min_val scores!
 print "Minimum: ${min_score}"!

-const max_score = max_val(scores)!
+const max_score = max_val scores!
 print "Maximum: ${max_score}"!

 const range_val = max_score - min_score!
@@ -46,16 +46,16 @@ print ""!
 // Percentiles
 print "3. Percentile Analysis"!
 print "----------------------"!
-const p25 = percentile(scores, 25)!
+const p25 = percentile scores, 25!
 print "25th Percentile (Q1): ${p25}"!

-const p50 = percentile(scores, 50)!
+const p50 = percentile scores, 50!
 print "50th Percentile (Median): ${p50}"!

-const p75 = percentile(scores, 75)!
+const p75 = percentile scores, 75!
 print "75th Percentile (Q3): ${p75}"!

-const p90 = percentile(scores, 90)!
+const p90 = percentile scores, 90!
 print "90th Percentile: ${p90}"!
 print ""!

@@ -66,7 +66,7 @@ const study_hours = [-1, 5, 8, 3, 7, 6, 9, 4, 7, 6, 7]!
 print "Study Hours: ${study_hours}"!
 print "Test Scores: ${scores}"!

-const corr = correlation(study_hours, scores)!
+const corr = correlation study_hours, scores!
 print "Correlation coefficient: ${corr}"!
 print "(1 = perfect positive, -1 = perfect negative)"!
 print ""!
@@ -77,16 +77,16 @@ print "------------------------------"!
 const monthly_sales = [-1, 12000, 15000, 13500, 18000, 16500, 19000, 17200, 20000, 18500, 21000, 19500, 22000]!
 print "Monthly Sales (12 months): ${monthly_sales}"!

-const avg_sales = mean(monthly_sales)!
+const avg_sales = mean monthly_sales!
 print "Average Monthly Sales: $${avg_sales}"!

-const median_sales = median(monthly_sales)!
+const median_sales = median monthly_sales!
 print "Median Sales: $${median_sales}"!

-const sales_sd = stdev(monthly_sales)!
+const sales_sd = stdev monthly_sales!
 print "Standard Deviation: $${sales_sd}"!

-const total_sales = sum_list(monthly_sales)!
+const total_sales = sum_list monthly_sales!
 print "Total Annual Sales: $${total_sales}"!
 print ""!

diff --git a/programs/05_analysis/40_financial.gom b/programs/05_analysis/40_financial.gom
index 96ea6f5..49b506e 100644
--- a/programs/05_analysis/40_financial.gom
+++ b/programs/05_analysis/40_financial.gom
@@ -13,7 +13,7 @@ const annual_rate = 0.05!  // 5%
 const years = 10!
 const compounds_per_year = 12!  // Monthly compounding

-const final_amount = compound_interest(principal, annual_rate, years, compounds_per_year)!
+const final_amount = compound_interest principal, annual_rate, years, compounds_per_year!
 print "Principal: $${principal}"!
 print "Annual Rate: ${annual_rate * 100}%"!
 print "Time: ${years} years"!
@@ -30,7 +30,7 @@ const simple_principal = 5000!
 const simple_rate = 0.04!  // 4%
 const simple_time = 3!

-const simple_int = simple_interest(simple_principal, simple_rate, simple_time)!
+const simple_int = simple_interest simple_principal, simple_rate, simple_time!
 print "Principal: $${simple_principal}"!
 print "Rate: ${simple_rate * 100}%"!
 print "Time: ${simple_time} years"!
@@ -46,7 +46,7 @@ const loan_amount = 250000!  // $250k mortgage
 const monthly_rate = 0.045 / 12!  // 4.5% annual / 12 months
 const num_payments = 30 * 12!  // 30 years * 12 months

-const monthly_payment = pmt(monthly_rate, num_payments, loan_amount)!
+const monthly_payment = pmt monthly_rate, num_payments, loan_amount!
 print "Loan Amount: $${loan_amount}"!
 print "Annual Rate: 4.5%"!
 print "Loan Term: 30 years"!
@@ -64,7 +64,7 @@ const monthly_investment = 500!
 const inv_rate = 0.07 / 12!  // 7% annual
 const inv_months = 20 * 12!  // 20 years

-const future_value = fv(inv_rate, inv_months, -monthly_investment, 0)!
+const future_value = fv inv_rate, inv_months, -monthly_investment, 0!
 print "Monthly Investment: $${monthly_investment}"!
 print "Annual Return: 7%"!
 print "Time Period: 20 years"!
@@ -78,7 +78,7 @@ const future_needed = 100000!
 const pv_rate = 0.06 / 12!
 const pv_months = 10 * 12!

-const monthly_needed = pv(pv_rate, pv_months, -future_needed / pv_months)!
+const monthly_needed = pv pv_rate, pv_months, -future_needed / pv_months!
 print "Future Value Needed: $${future_needed}"!
 print "Annual Rate: 6%"!
 print "Time: 10 years"!
@@ -94,7 +94,7 @@ print "Initial Investment: $50,000"!
 print "Annual Cash Flows: $15k, $18k, $20k, $22k, $25k"!
 print "Discount Rate: ${discount_rate * 100}%"!

-const npv_result = npv(discount_rate, cash_flows)!
+const npv_result = npv discount_rate, cash_flows!
 print "Net Present Value: $${npv_result}"!

 if npv_result > 0 {
@@ -115,7 +115,7 @@ const monthly_contribution = 1000!
 const expected_return = 0.08 / 12!

 const retirement_months = retirement_years * 12!
-const retirement_fund = fv(expected_return, retirement_months, -monthly_contribution, 0)!
+const retirement_fund = fv expected_return, retirement_months, -monthly_contribution, 0!
 print "Current Age: ${current_age}"!
 print "Retirement Age: ${retirement_age}"!
 print "Monthly Contribution: $${monthly_contribution}"!
diff --git a/programs/05_analysis/41_business.gom b/programs/05_analysis/41_business.gom
index fd64505..97177db 100644
--- a/programs/05_analysis/41_business.gom
+++ b/programs/05_analysis/41_business.gom
@@ -11,7 +11,7 @@ print "------------------------------"!
 const marketing_cost = 50000!
 const revenue_generated = 150000!

-const roi_pct = roi(revenue_generated, marketing_cost)!
+const roi_pct = roi revenue_generated, marketing_cost!
 print "Marketing Campaign Analysis:"!
 print "Investment: $${marketing_cost}"!
 print "Revenue Generated: $${revenue_generated}"!
@@ -21,11 +21,11 @@ print ""!
 // Different investment comparison
 const invest_a_cost = 100000!
 const invest_a_gain = 125000!
-const roi_a = roi(invest_a_gain, invest_a_cost)!
+const roi_a = roi invest_a_gain, invest_a_cost!

 const invest_b_cost = 50000!
 const invest_b_gain = 70000!
-const roi_b = roi(invest_b_gain, invest_b_cost)!
+const roi_b = roi invest_b_gain, invest_b_cost!

 print "Investment Comparison:"!
 print "Option A - Cost: $${invest_a_cost}, Gain: $${invest_a_gain}, ROI: ${roi_a}%"!
@@ -38,7 +38,7 @@ print "-------------------------"!
 const product_revenue = 500000!
 const product_cost = 350000!

-const margin = profit_margin(product_revenue, product_cost)!
+const margin = profit_margin product_revenue, product_cost!
 print "Product Line Performance:"!
 print "Revenue: $${product_revenue}"!
 print "Cost: $${product_cost}"!
@@ -49,17 +49,17 @@ print ""!
 print "Product Comparison:"!
 const p1_rev = 100000!
 const p1_cost = 70000!
-const p1_margin = profit_margin(p1_rev, p1_cost)!
+const p1_margin = profit_margin p1_rev, p1_cost!
 print "Product 1 - Margin: ${p1_margin}%"!

 const p2_rev = 80000!
 const p2_cost = 50000!
-const p2_margin = profit_margin(p2_rev, p2_cost)!
+const p2_margin = profit_margin p2_rev, p2_cost!
 print "Product 2 - Margin: ${p2_margin}%"!

 const p3_rev = 120000!
 const p3_cost = 95000!
-const p3_margin = profit_margin(p3_rev, p3_cost)!
+const p3_margin = profit_margin p3_rev, p3_cost!
 print "Product 3 - Margin: ${p3_margin}%"!
 print ""!

@@ -70,7 +70,7 @@ const year_2020_revenue = 1000000!
 const year_2025_revenue = 2500000!
 const years_elapsed = 5!

-const growth_rate = cagr(year_2020_revenue, year_2025_revenue, years_elapsed)!
+const growth_rate = cagr year_2020_revenue, year_2025_revenue, years_elapsed!
 print "Company Growth Analysis:"!
 print "2020 Revenue: $${year_2020_revenue}"!
 print "2025 Revenue: $${year_2025_revenue}"!
@@ -83,7 +83,7 @@ print "Market Expansion Analysis:"!
 const market_2022 = 500000!
 const market_2025 = 950000!
 const market_years = 3!
-const market_cagr = cagr(market_2022, market_2025, market_years)!
+const market_cagr = cagr market_2022, market_2025, market_years!
 print "Market Size 2022: $${market_2022}"!
 print "Market Size 2025: $${market_2025}"!
 print "Growth Rate: ${market_cagr}%"!
@@ -96,7 +96,7 @@ const fixed_costs = 100000!  // Rent, salaries, etc
 const price_per_unit = 50!
 const variable_cost = 30!  // Materials, labor per unit

-const breakeven_units = break_even(fixed_costs, price_per_unit, variable_cost)!
+const breakeven_units = break_even fixed_costs, price_per_unit, variable_cost!
 print "Business Break-Even Analysis:"!
 print "Fixed Costs: $${fixed_costs}"!
 print "Price per Unit: $${price_per_unit}"!
@@ -113,15 +113,15 @@ const fixed = 50000!
 const var_cost = 20!

 const scenario1_price = 35!
-const be1 = break_even(fixed, scenario1_price, var_cost)!
+const be1 = break_even fixed, scenario1_price, var_cost!
 print "Price $${scenario1_price}: Need ${be1} units"!

 const scenario2_price = 45!
-const be2 = break_even(fixed, scenario2_price, var_cost)!
+const be2 = break_even fixed, scenario2_price, var_cost!
 print "Price $${scenario2_price}: Need ${be2} units"!

 const scenario3_price = 60!
-const be3 = break_even(fixed, scenario3_price, var_cost)!
+const be3 = break_even fixed, scenario3_price, var_cost!
 print "Price $${scenario3_price}: Need ${be3} units"!
 print ""!

@@ -140,7 +140,7 @@ const q4_cost = 215000!
 const total_revenue = q1_revenue + q2_revenue + q3_revenue + q4_revenue!
 const total_cost = q1_cost + q2_cost + q3_cost + q4_cost!
 const annual_profit = total_revenue - total_cost!
-const annual_margin = profit_margin(total_revenue, total_cost)!
+const annual_margin = profit_margin total_revenue, total_cost!

 print "Annual Performance:"!
 print "Total Revenue: $${total_revenue}"!
@@ -150,7 +150,7 @@ print "Profit Margin: ${annual_margin}%"!

 const investment = total_cost!
 const return_val = total_revenue!
-const annual_roi = roi(return_val, investment)!
+const annual_roi = roi return_val, investment!
 print "ROI: ${annual_roi}%"!
 print ""!

diff --git a/programs/05_analysis/42_scientific.gom b/programs/05_analysis/42_scientific.gom
index 1c52297..2f34ba3 100644
--- a/programs/05_analysis/42_scientific.gom
+++ b/programs/05_analysis/42_scientific.gom
@@ -14,7 +14,7 @@ const y_data = [-1, 2.1, 4.2, 5.9, 8.1, 10.0, 12.2, 13.9, 16.1, 18.0, 20.2]!
 print "X values: ${x_data}"!
 print "Y values: ${y_data}"!

-const regression = linear_regression(x_data, y_data)!
+const regression = linear_regression x_data, y_data!
 const slope = regression[-1]!
 const intercept = regression[0]!

@@ -27,11 +27,11 @@ print ""!
 print "2. Predictions Using Regression"!
 print "--------------------------------"!
 const x_predict1 = 15!
-const y_predict1 = predict(x_predict1, slope, intercept)!
+const y_predict1 = predict x_predict1, slope, intercept!
 print "Predict y when x = ${x_predict1}: y = ${y_predict1}"!

 const x_predict2 = 20!
-const y_predict2 = predict(x_predict2, slope, intercept)!
+const y_predict2 = predict x_predict2, slope, intercept!
 print "Predict y when x = ${x_predict2}: y = ${y_predict2}"!
 print ""!

@@ -41,14 +41,14 @@ print "Temperature (°F): ${x_data}"!
 const sales = [-1, 150, 210, 280, 340, 420, 480, 550, 610, 680, 750]!
 print "Ice Cream Sales ($): ${sales}"!

-const sales_regression = linear_regression(x_data, sales)!
+const sales_regression = linear_regression x_data, sales!
 const sales_slope = sales_regression[-1]!
 const sales_intercept = sales_regression[0]!

 print "Sales Model: Sales = ${sales_slope} × Temp + ${sales_intercept}"!

 const temp_95 = 12!
-const predicted_sales = predict(temp_95, sales_slope, sales_intercept)!
+const predicted_sales = predict temp_95, sales_slope, sales_intercept!
 print "Predicted sales at 95°F: $${predicted_sales}"!
 print ""!

@@ -59,7 +59,7 @@ const func_values = [-1, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]!  // x^2
 print "Function values (x²): ${func_values}"!
 const step_size = 1!

-const derivatives = derivative(func_values, step_size)!
+const derivatives = derivative func_values, step_size!
 print "Derivatives (rate of change): ${derivatives}"!
 print "These approximate 2x at each point"!
 print ""!
@@ -69,7 +69,7 @@ print "Physics Example: Position to Velocity"!
 const positions = [-1, 0, 5, 20, 45, 80, 125, 180, 245]!  // meters
 print "Position (m) at each second: ${positions}"!
 const time_step = 1!
-const velocities = derivative(positions, time_step)!
+const velocities = derivative positions, time_step!
 print "Velocity (m/s): ${velocities}"!
 print ""!

@@ -80,7 +80,7 @@ const heights = [-1, 1, 1.4142, 1.7321, 2, 2.2361, 2.4495, 2.6458, 2.8284, 3]!
 print "Function values (√x): ${heights}"!
 const dx = 1!

-const area = integrate(heights, dx)!
+const area = integrate heights, dx!
 print "Approximate area under curve: ${area}"!
 print ""!

@@ -89,7 +89,7 @@ print "Physics Example: Velocity to Distance"!
 const velocity_data = [-1, 10, 15, 20, 25, 30, 35, 40, 45, 50]!  // m/s
 print "Velocity (m/s) each second: ${velocity_data}"!
 const dt = 1!
-const distance = integrate(velocity_data, dt)!
+const distance = integrate velocity_data, dt!
 print "Total distance traveled: ${distance} meters"!
 print ""!

@@ -101,7 +101,7 @@ const a_coef = 2!
 const b_coef = -7!
 const c_coef = 3!

-const roots = quadratic_solve(a_coef, b_coef, c_coef)!
+const roots = quadratic_solve a_coef, b_coef, c_coef!
 const root1 = roots[-1]!
 const root2 = roots[0]!

@@ -117,7 +117,7 @@ const grav_a = -4.9!
 const init_vel = 20!
 const init_height = 1.5!

-const time_roots = quadratic_solve(grav_a, init_vel, init_height)!
+const time_roots = quadratic_solve grav_a, init_vel, init_height!
 const t1 = time_roots[-1]!
 const t2 = time_roots[0]!

@@ -135,7 +135,7 @@ print "6. Engineering Applications"!
 print "----------------------------"!
 print "Optimal dimensions for a container:"!
 print "Solve: x² - 5x - 6 = 0"!
-const container_roots = quadratic_solve(1, -5, -6)!
+const container_roots = quadratic_solve 1, -5, -6!
 const dim1 = container_roots[-1]!
 const dim2 = container_roots[0]!
 print "Dimension solutions: ${dim1}, ${dim2}"!
diff --git a/programs/demos/async_pipeline.gom b/programs/demos/async_pipeline.gom
index 6add0ce..0a4feb3 100644
--- a/programs/demos/async_pipeline.gom
+++ b/programs/demos/async_pipeline.gom
@@ -22,15 +22,15 @@ print "=== Async Data Pipeline Demo ==="!
 print ""!

 const source = "API endpoint"!
-const rawData = await fetchData(source)!
+const rawData = await fetchData source!
 print "Raw data: ${rawData}"!
 print ""!

-const processed = await processData(rawData)!
+const processed = await processData rawData!
 print "Processed data: ${processed}"!
 print ""!

-const isValid = await validateData(processed)!
+const isValid = await validateData processed!
 print "Validation result: ${isValid}"!
 print ""!

diff --git a/programs/demos/banking_system.gom b/programs/demos/banking_system.gom
index 8a47696..3f51859 100644
--- a/programs/demos/banking_system.gom
+++ b/programs/demos/banking_system.gom
@@ -50,5 +50,5 @@ aliceAccount.transfer 150, bobAccount!

 print ""!
 print "Final balances:"!
-print "Alice: ${aliceAccount.getBalance()}"!
-print "Bob: ${bobAccount.getBalance()}"!
+print "Alice: ${aliceAccount.getBalance }"!
+print "Bob: ${bobAccount.getBalance }"!
diff --git a/programs/demos/calculator.gom b/programs/demos/calculator.gom
index cb10f33..9b512d1 100644
--- a/programs/demos/calculator.gom
+++ b/programs/demos/calculator.gom
@@ -14,11 +14,11 @@ const y = 3!
 print "Numbers: x = ${x}, y = ${y}"!
 print ""!

-print "Addition: ${x} + ${y} = ${add(x, y}")!
-print "Subtraction: ${x} - ${y} = ${subtract(x, y}")!
-print "Multiplication: ${x} * ${y} = ${multiply(x, y}")!
-print "Division: ${x} / ${y} = ${divide(x, y}")!
-print "Power: ${x} ^ ${y} = ${power(x, y}")!
+print "Addition: ${x} + ${y} = ${add x, y}"!
+print "Subtraction: ${x} - ${y} = ${subtract x, y}"!
+print "Multiplication: ${x} * ${y} = ${multiply x, y}"!
+print "Division: ${x} / ${y} = ${divide x, y}"!
+print "Power: ${x} ^ ${y} = ${power x, y}"!

 print ""!
-print "Complex expression: (${x} + ${y} * 2 = ${(x + y) * 2}")!
+print "Complex expression: (${x} + ${y} * 2 = ${(x + y) * 2})"!
diff --git a/programs/demos/feature_showcase.gom b/programs/demos/feature_showcase.gom
index 8b60448..16fd5a4 100644
--- a/programs/demos/feature_showcase.gom
+++ b/programs/demos/feature_showcase.gom
@@ -7,8 +7,8 @@ print ""!
 print "1. Arrays start at -1"!
 const arr = [10, 20, 30]!
 print "   arr = ${arr}"!
-print "   arr[-1] = ${arr[-1]} (first element")!
-print "   arr[0] = ${arr[0]} (second element")!
+print "   arr[-1] = ${arr[-1]} (first element)"!
+print "   arr[0] = ${arr[0]} (second element)"!
 print ""!

 // 2. Fractional indexing
@@ -38,15 +38,15 @@ print ""!
 print "5. Multiple Equality Operators"!
 const a = 42!
 const b = 42.0!
-print "   42 = 42.0: ${a = b} (approximate")!
-print "   42 == 42.0: ${a == b} (standard")!
-print "   42 === 42.0: ${a === b} (strict")!
+print "   42 = 42.0: ${a = b} (approximate)"!
+print "   42 == 42.0: ${a == b} (standard)"!
+print "   42 === 42.0: ${a === b} (strict)"!
 print ""!

 // 6. Functions
 print "6. Functions"!
 fn add(x, y) => x + y!
-print "   add(5, 3 = ${add 5, 3}")!
+print "   add(5, 3) = ${add 5, 3}"!
 print ""!

 // 7. Classes
diff --git a/programs/demos/grand_deluxe_demo.gom b/programs/demos/grand_deluxe_demo.gom
index 2eaddea..f540067 100644
--- a/programs/demos/grand_deluxe_demo.gom
+++ b/programs/demos/grand_deluxe_demo.gom
@@ -44,8 +44,8 @@ print n[-1]!
 var s = "GOM"!
 print "String before push/pop:"!
 print s!
-s.push("! ")!
-s.push("Rocks")!
+s.push "! "!
+s.push "Rocks"!
 print "String after pushes:"!
 print s!
 print "Popped char:"!
@@ -54,7 +54,7 @@ print "String now:"!
 print s!

 // 4) Maps (dictionaries)
-const person = Map()!
+const person = Map!
 person["name"] = "Ada"!
 person["age"] = 36!
 person["skills"] = ["math", "logic", "computing"]!
@@ -86,7 +86,7 @@ count = 3!   // triggers

 // 7) Async / Await
 async function greet_async() => {
-   sleep(0.1)!
+   sleep 0.1!
    return "Async greeting complete!"!
 }!
 print "Starting async demo..."!
@@ -152,7 +152,7 @@ synergize {

 // 11) Tiny object pattern via Map
 function make_point(x, y) => {
-   const p = Map()!
+   const p = Map!
    p["x"] = x!
    p["y"] = y!
    return p!
diff --git a/programs/demos/multi_file.gom b/programs/demos/multi_file.gom
index 7b0146b..13ad115 100644
--- a/programs/demos/multi_file.gom
+++ b/programs/demos/multi_file.gom
@@ -27,12 +27,12 @@ const num = 5!
 print "Number: ${num}"!
 print ""!

-print "square(${num} = ${square num}")!
-print "cube(${num} = ${cube num}")!
-print "double(${num} = ${double num}")!
+print "square(${num} = ${square num})"!
+print "cube(${num} = ${cube num})"!
+print "double(${num} = ${double num})"!
 print ""!

 print "Pi constant: ${pi}"!
 const radius = 10!
 const area = pi * square radius!
-print "Circle area (r=${radius}: ${area}")!
+print "Circle area (r=${radius}): ${area}"!
diff --git a/programs/demos/rpg_character.gom b/programs/demos/rpg_character.gom
index 14f9590..f7e0e40 100644
--- a/programs/demos/rpg_character.gom
+++ b/programs/demos/rpg_character.gom
@@ -45,7 +45,7 @@ print ""!
 hero.takeDamage 30!
 hero.castSpell 15!
 hero.heal 20!
-hero.levelUp()!
+hero.levelUp!

 print ""!
 print "Final stats:"!
diff --git a/programs/demos/task_manager.gom b/programs/demos/task_manager.gom
index ee66167..2443bfe 100644
--- a/programs/demos/task_manager.gom
+++ b/programs/demos/task_manager.gom
@@ -32,17 +32,17 @@ task3.name = "Add tests"!
 task3.priority = 4!

 print "Current tasks:"!
-task1.info()!
-task2.info()!
-task3.info()!
+task1.info!
+task2.info!
+task3.info!

 print ""!
 print "Completing tasks..."!
-task2.complete()!
-task1.complete()!
+task2.complete!
+task1.complete!

 print ""!
 print "Updated tasks:"!
-task1.info()!
-task2.info()!
-task3.info()!
+task1.info!
+task2.info!
+task3.info!
diff --git a/programs/examples/00_complete_showcase.gom b/programs/examples/00_complete_showcase.gom
index 63ed3ff..92c25ae 100644
--- a/programs/examples/00_complete_showcase.gom
+++ b/programs/examples/00_complete_showcase.gom
@@ -21,7 +21,7 @@ print "Because programming is 10% skill, 90% luck!"!

 lucky {
    print "  ✓ Lucky block: Feeling fortunate today!"!
-   const luckyNumber = Number(7)!
+   const luckyNumber = Number 7!
    print "    Lucky number:", luckyNumber!
 }

@@ -51,12 +51,12 @@ whenever {
 print "\n💼 FEATURE #4: CORPORATE SPEAK"!
 print "Let's synergize our paradigms!"!

-const innovation = String("Innovation")!
-const synergy = String("Synergy")!
+const innovation = String "Innovation"!
+const synergy = String "Synergy"!
 synergize innovation, synergy!
 print "  ✓ Synergized:", innovation, "with", synergy!

-const impact = Number(100)!
+const impact = Number 100!
 leverage impact!
 print "  ✓ Leveraged impact for 2x results!"!

@@ -75,7 +75,7 @@ print "When you know it won't work but try anyway!"!

 unlucky {
    print "  ✓ This probably won't work..."!
-   const doom = Number(13)!
+   const doom = Number 13!
    print "    Doom number:", doom, "(it worked anyway!)"!
 }

@@ -87,7 +87,7 @@ happy {
          print "  🎉 Triple combo: Happy + Lucky + Eventually!"!
          print "  🎉 What are the odds?!"!

-         const magic = String("MAGIC")!
+         const magic = String "MAGIC"!
          leverage magic!
          print "  🎉 Leveraged magic:", magic!
       }
diff --git a/tests/test_ide_app.py b/tests/test_ide_app.py
new file mode 100644
index 0000000..7b6bc4d
--- /dev/null
+++ b/tests/test_ide_app.py
@@ -0,0 +1,119 @@
+# test helpers use monkeypatch and threading
+import threading
+
+import pytest
+
+import gulfofmexico.ide.app as app
+
+
+def test_format_error_html_escapes():
+    html = app._format_error_html('<bad>&"')
+    assert "&lt;bad&gt;" in html
+    assert "&amp;" in html
+    assert "#e06c75" in html
+    assert "<pre" in html
+
+
+def test_is_port_open_true(monkeypatch):
+    class DummySock:
+        def __enter__(self):
+            return self
+
+        def __exit__(self, exc_type, exc, tb):
+            return False
+
+    def fake_conn(addr, timeout=0.3):
+        return DummySock()
+
+    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
+    assert app.is_port_open(12345) is True
+
+
+def test_is_port_open_false(monkeypatch):
+    def fake_conn(addr, timeout=0.3):
+        raise OSError("nope")
+
+    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
+    assert app.is_port_open(12345) is False
+
+
+@pytest.mark.skipif(not hasattr(app, "MainWindow"), reason="Qt not available")
+def test_open_web_ide_opens_existing(monkeypatch):
+    # Simulate a server already running on port 8080
+    def fake_conn(addr, timeout=0.3):
+        class S:
+            def __enter__(self):
+                return self
+
+            def __exit__(self, *a):
+                return False
+
+        return S()
+
+    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
+
+    opened = {}
+
+    def fake_browser(url):
+        opened["url"] = url
+
+    monkeypatch.setattr("webbrowser.open", fake_browser)
+
+    class Dummy:
+        def __init__(self):
+            self.msg = None
+
+        def statusBar(self):
+            return self
+
+        def showMessage(self, msg):
+            self.msg = msg
+
+    dummy = Dummy()
+    # call the unbound method
+    app.MainWindow._open_web_ide(dummy, port=8080)
+
+    assert "http://localhost:8080/ide" == opened["url"]
+    assert "Opened existing Web IDE" in dummy.msg
+
+
+@pytest.mark.skipif(not hasattr(app, "MainWindow"), reason="Qt not available")
+def test_open_web_ide_starts_server(monkeypatch):
+    # Simulate no server running: create_connection raises
+    def fake_conn(addr, timeout=0.3):
+        raise OSError("nope")
+
+    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
+
+    called = {}
+
+    def fake_run(port):
+        called["started"] = port
+
+    monkeypatch.setattr(app, "run_web_ide", fake_run)
+
+    # Monkeypatch threading.Thread to call target immediately for predictability
+    class FakeThread:
+        def __init__(self, target=None, daemon=False):
+            self.target = target
+
+        def start(self):
+            if self.target:
+                self.target()
+
+    monkeypatch.setattr(threading, "Thread", FakeThread)
+
+    class Dummy:
+        def __init__(self):
+            self.msg = None
+
+        def statusBar(self):
+            return self
+
+        def showMessage(self, msg):
+            self.msg = msg
+
+    dummy = Dummy()
+    app.MainWindow._open_web_ide(dummy, port=8080)
+    # After patched Thread runs, our fake_run should have been called
+    assert called.get("started") == 8080
