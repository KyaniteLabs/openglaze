/**
 * OpenGlaze Data - Community glaze database with chemistry, recipes, and combinations
 * 32 community glazes organized by color family
 *
 * All glaze names are generic/descriptive. Recipes are from published ceramic
 * literature, traditional formulations, or publicly shared community recipes.
 * No studio-specific names, commercial product codes, or proprietary formulas.
 *
 * COLORANT RULES: Based on research from DigitalFire, Ceramic Arts Network,
 * John Britt, Glazy.org, Ceramic Materials Workshop, and peer-reviewed
 * ceramic science literature.
 */

const FAMILY_ORDER = ['Reds', 'Yellows', 'Greens', 'Blues', 'Purples', 'Browns', 'Neutrals', 'Whites', 'Clears', 'Shinos', 'Crystals', 'Reactive'];

const COLORANT_RULES = [
    // === IRON ===
    { id: 'iron-reduction-green', rule: 'Iron 1-2% in reduction = celadon/jade green. More iron (3-5%) = darker olive to iron red.', confidence: 'high' },
    { id: 'iron-oxidation-amber', rule: 'Iron in oxidation = amber, brown, tan. Same iron in reduction = green, black, or red.', confidence: 'high' },
    { id: 'iron-high-saturation', rule: 'High iron (8%+) in reduction = tenmoku black with amber breaks. Very predictable.', confidence: 'high' },
    { id: 'iron-kills-copper-red', rule: 'Iron suppresses copper red. Copper red needs iron-free bases. Iron + copper = muddy brown.', confidence: 'high' },
    { id: 'iron-plus-cobalt', rule: 'Iron shifts cobalt from pure blue toward blue-green/teal.', confidence: 'high' },

    // === COPPER ===
    { id: 'copper-reduction-red', rule: 'Copper 0.5-1.5% in heavy reduction = copper red (sang de boeuf). Needs tin oxide 1-2%.', confidence: 'high' },
    { id: 'copper-oxidation-green', rule: 'Copper in oxidation = green (turquoise to emerald). Same copper in reduction = red or purple.', confidence: 'high' },
    { id: 'copper-plus-zinc-green', rule: 'Copper + zinc = turquoise green. Zinc enhances copper greens but destroys copper reds.', confidence: 'high' },
    { id: 'copper-plus-iron', rule: 'Copper over iron-rich glaze = brown/muddy, not purple. Iron interferes with copper color development.', confidence: 'high' },
    { id: 'copper-reduction-sensitive', rule: 'Copper red is extremely reduction-sensitive. Too little reduction = green. Too much = murky metallic.', confidence: 'high' },

    // === COBALT ===
    { id: 'cobalt-stable-blue', rule: 'Cobalt is the most predictable colorant. Always produces blue in any atmosphere.', confidence: 'high' },
    { id: 'cobalt-over-white', rule: 'Cobalt over white/opaque base = bright, clean blue. The best way to get vivid blue.', confidence: 'high' },
    { id: 'cobalt-over-iron', rule: 'Cobalt over iron base = blue-green to dark navy. Iron shifts cobalt toward green.', confidence: 'high' },
    { id: 'cobalt-plus-manganese', rule: 'Cobalt + manganese = purple-toned blue. Classic combination for purples.', confidence: 'high' },
    { id: 'cobalt-plus-zinc', rule: 'Cobalt in zinc-rich bases = muted violet-blue. Zinc dulls cobalt.', confidence: 'medium' },
    { id: 'cobalt-plus-rutile', rule: 'Cobalt + rutile = mottled, streaky blue with variegation.', confidence: 'medium' },

    // === CHROME ===
    { id: 'chrome-alone-green', rule: 'Chrome oxide alone = green. Stable and predictable in oxidation.', confidence: 'high' },
    { id: 'chrome-tin-pink', rule: 'Chrome 0.2-0.5% + tin 1.5-2% = pink (chrome-tin pink). Needs zinc-free base.', confidence: 'high' },
    { id: 'chrome-zinc-kills-pink', rule: 'Zinc DESTROYS chrome-tin pink. Even small zinc amounts turn pink to brown. Critical rule.', confidence: 'high' },
    { id: 'chrome-zinc-brown', rule: 'Chrome + zinc = brown (not green). Zinc transforms chrome green to brown.', confidence: 'high' },

    // === MANGANESE ===
    { id: 'manganese-oxidation-purple', rule: 'Manganese in oxidation = purple to brown. In reduction = brown, metallic effects.', confidence: 'high' },
    { id: 'manganese-plus-cobalt', rule: 'Manganese + cobalt = purple. The classic purple combination.', confidence: 'high' },
    { id: 'manganese-plus-iron', rule: 'Manganese + iron = deep brown to black. Darkens significantly.', confidence: 'high' },
    { id: 'manganese-high-blister', rule: 'High manganese (>3%) can cause blistering and surface defects.', confidence: 'medium' },

    // === ZINC ===
    { id: 'zinc-color-killer', rule: 'Zinc kills: chrome-tin pink, chrome green. Zinc enhances: copper green, crystallization.', confidence: 'high' },
    { id: 'zinc-preserves-red', rule: 'Zinc-free clears preserve copper red. Zinc-containing clears can shift red.', confidence: 'high' },

    // === RUTILE / TITANIUM ===
    { id: 'rutile-variegation', rule: 'Rutile (TiO2 + iron) creates variegation, mottling, and micro-crystals. Unpredictable but beautiful.', confidence: 'high' },
    { id: 'rutile-plus-iron', rule: 'Rutile + iron = blue-green to teal effects. Titanium-iron interaction.', confidence: 'medium' },
    { id: 'rutile-plus-cobalt', rule: 'Rutile + cobalt = streaky, mottled blue. Titanium disrupts uniform cobalt color.', confidence: 'medium' },
    { id: 'rutile-phototropy', rule: 'Rutile can cause phototropy — glaze looks different colors in different lighting.', confidence: 'medium' },

    // === SHINOS ===
    { id: 'shino-goes-first', rule: 'SHINOS MUST BE THE BASE LAYER. Shino over almost any other glaze crawls or looks terrible.', confidence: 'high' },
    { id: 'shino-carbon-trap', rule: 'Shinos trap carbon in reduction. Thin application = more orange. Thick = more white/gray.', confidence: 'high' },
    { id: 'shino-under-celadon', rule: 'Celadon over shino = jade green with carbon trap patterns showing through. Classic combo.', confidence: 'high' },
    { id: 'shino-under-tenmoku', rule: 'Tenmoku over shino = dark iron pools over warm carbon trap texture.', confidence: 'high' },

    // === TENMOKU ===
    { id: 'tenmoku-iron-rich', rule: 'Tenmoku has 8-10% iron. It dominates any glaze layered over it — expect darkening.', confidence: 'high' },
    { id: 'tenmoku-amber-breaks', rule: 'Tenmoku breaks amber/gold where thin. Over white base, breaks are more visible.', confidence: 'high' },
    { id: 'tenmoku-plus-chun', rule: 'Chun Blue (copper+iron) over Tenmoku = purple flash at boundary where both glazes interact.', confidence: 'high' },

    // === LAYERING PRINCIPLES ===
    { id: 'opaque-under-transparent', rule: 'Opaque base + transparent top = clean, bright color. The best general-purpose layering strategy.', confidence: 'high' },
    { id: 'dark-under-light', rule: 'Dark glaze under light = the dark shows through. Light glaze under dark = dark dominates.', confidence: 'high' },
    { id: 'fluid-over-stiff', rule: 'Fluid glaze over stiff glaze = pooling in recesses, crawling on high spots. Texture matters.', confidence: 'high' },
    { id: 'high-iron-warning', rule: 'Both glazes high in iron = very dark, muddy result. Limit iron to one layer.', confidence: 'high' },
];

const DATA = {
    research_backed: [
        // === SHINO-BASED COMBOS (all well-documented) ===
        {
            id: 1,
            top: "Celadon",
            base: "Classic Shino",
            result: "Jade green with warm orange/gray carbon trap patterns showing through thin areas",
            chemistry: "Shino as base prevents crawling; carbon trap shows through translucent celadon; iron in celadon (1-2%) doesn't conflict with shino",
            bestOn: "Textured surfaces, carved decoration",
            risk: "low",
            prediction_grade: "likely",
            application: "Shino base (even coat) → Celadon over (thin to medium)",
            confidence: "high",
            source: "Classic combo — documented across multiple sources"
        },
        {
            id: 2,
            top: "Tenmoku",
            base: "Carbon Trap Shino",
            result: "Dark brown/black tenmoku pooling in recesses over iridescent orange/gray shino",
            chemistry: "Shino as base prevents crawling; high-iron tenmoku pools in texture; warm shino shows through where tenmoku thins",
            bestOn: "Sculptural pieces, forms with texture",
            risk: "low",
            prediction_grade: "likely",
            application: "Carbon Trap Shino base → Tenmoku over (thin on high spots)",
            confidence: "high",
            source: "Well-documented shino-under-dark-glaze combo"
        },
        {
            id: 3,
            top: "Chun Blue",
            base: "Classic Shino",
            result: "Blue pooling over warm carbon trap shino; cool-warm contrast where Chun is thicker",
            chemistry: "Shino as base prevents crawling; Chun (copper+iron) creates blue tones contrasting with warm shino oranges",
            bestOn: "Vases, tall forms",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Standard shino-under-fluid-glaze pattern"
        },
        {
            id: 4,
            top: "Iron Red",
            base: "Carbon Trap Shino",
            result: "Rust red breaking over iridescent shino texture with warm metallic undertones",
            chemistry: "Iron red (8-12% iron) breaks nicely over shino texture; both are warm-toned glazes",
            bestOn: "Accent pieces, decorative ware",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "High-iron glaze over shino — documented pattern"
        },
        {
            id: 5,
            top: "Iron Luster",
            base: "Classic Shino",
            result: "Golden amber over warm carbon trap; potentially monotone warm-on-warm",
            chemistry: "Both iron-based warm glazes; similar color temperature may lack contrast",
            bestOn: "Simple forms where subtle warmth works",
            risk: "low",
            prediction_grade: "possible",
            confidence: "medium",
            warning: "May lack visual contrast — two warm glazes can blend together"
        },
        {
            id: 6,
            top: "Jade Green",
            base: "Classic Shino",
            result: "Opaque jade green over orange/gray carbon trap patterns",
            chemistry: "Jade green is opaque iron green (3-5% iron in reduction); higher opacity than celadon so less shino shows through",
            bestOn: "Bold pieces where strong color contrast is desired",
            risk: "low",
            prediction_grade: "possible",
            confidence: "medium",
            source: "Similar to celadon-over-shino but more opaque"
        },

        // === WHITE-BASED COMBOS (opaque under transparent = clean color) ===
        {
            id: 7,
            top: "Copper Red",
            base: "Opaque White",
            result: "Bright copper red with clean white breaks at edges",
            chemistry: "White base ensures clean copper red development; zirconium white reflects light through copper red; breaks white where thin",
            bestOn: "Rims, edges where breaking shows",
            risk: "medium",
            prediction_grade: "likely",
            warning: "Copper red needs heavy reduction — if reduction is weak, turns green/gray",
            application: "Opaque White base → Copper Red over",
            confidence: "high",
            source: "Classic copper red over white — textbook combo"
        },
        {
            id: 8,
            top: "Panama Red",
            base: "High-Opacity White",
            result: "Blood red to tomato red with clean white breaks",
            chemistry: "High-opacity white ensures clean breaks for copper red; Panama Red has slightly more copper than standard Copper Red",
            bestOn: "Functional ware where vivid red is desired",
            risk: "medium",
            prediction_grade: "likely",
            warning: "Requires heavy reduction — oxidized = gray/green",
            confidence: "high",
            source: "Copper red over opaque white — well-documented"
        },
        {
            id: 9,
            top: "Copper-Cobalt Blue",
            base: "High-Opacity White",
            result: "Complex blue with depth from copper/cobalt blend against bright white",
            chemistry: "Cobalt + copper over white = clean, bright blue. White base maximizes color intensity.",
            bestOn: "Any form where vivid blue is desired",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Cobalt-based blue over white — most predictable combo type"
        },
        {
            id: 10,
            top: "Cobalt Blue",
            base: "Opaque White",
            result: "Clean, stable cobalt blue over white",
            chemistry: "Cobalt (0.5-1%) over white = most reliable blue in ceramics. Cobalt is atmosphere-stable.",
            bestOn: "Any form, especially functional ware",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Cobalt over white — the most predictable ceramic color"
        },
        {
            id: 11,
            top: "Copper Green",
            base: "Opaque White",
            result: "Bright grass green to emerald over white; cleaner than over dark bases",
            chemistry: "Copper green (2-3% copper) over white = brighter, cleaner green. White base prevents darkening.",
            bestOn: "Pieces where vivid green is desired",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Copper green over opaque base — standard approach"
        },

        // === CLEAR-OVER-COLOR COMBOS (gloss protection, no color shift) ===
        {
            id: 12,
            top: "Zinc-Free Clear",
            base: "Copper Red",
            result: "Copper red with added gloss and surface protection, no color shift",
            chemistry: "Zinc-free clear preserves true copper red color. Zinc-containing clears would risk shifting red toward brown.",
            bestOn: "Functional ware, any form",
            risk: "low",
            prediction_grade: "likely",
            application: "Copper Red base → Zinc-Free Clear over",
            confidence: "high",
            source: "Zinc-free clear over copper red — standard protection"
        },
        {
            id: 13,
            top: "Zinc-Free Clear",
            base: "Manganese Purple",
            result: "Manganese-cobalt purple with added gloss, no color shift",
            chemistry: "Zinc-free clear adds gloss without modifying manganese-cobalt purple",
            bestOn: "Decorative pieces where glossy purple is desired",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Clear over stable purple — straightforward"
        },
        {
            id: 14,
            top: "Chrome-Tin Pink",
            base: "Opaque White",
            result: "Soft coral to rose pink with clean white base showing through at breaks",
            chemistry: "Chrome-tin pink NEEDS white base (zinc-free) to develop properly. Opaque White has no zinc.",
            bestOn: "Delicate pieces, functional ware",
            risk: "medium",
            prediction_grade: "likely",
            warning: "Chrome-tin pink needs oxidation for best color; reduction may shift toward gray-green. Zinc destroys this color.",
            confidence: "high",
            source: "Chrome-tin pink over zinc-free white — well-documented requirement"
        },

        // === IRON-RICH COMBOS ===
        {
            id: 15,
            top: "Chun Blue",
            base: "Tenmoku",
            result: "Dark brown/black base with purple flash where Chun and Tenmoku interact at the boundary",
            chemistry: "Chun (copper+iron) over high-iron Tenmoku — both are iron-rich. The purple flash happens where copper from Chun meets iron from Tenmoku. Where Chun thins, Tenmoku's amber shows through.",
            bestOn: "Rims, bowls, vertical forms with thin edges",
            risk: "medium",
            prediction_grade: "likely",
            warning: "Run potential — both glazes are fluid. Watch thickness on vertical surfaces.",
            application: "Tenmoku base (thin) → Chun Blue over",
            confidence: "high",
            source: "Well-documented classic combo — copper+iron interaction"
        },
        {
            id: 16,
            top: "Chun Blue",
            base: "Crawling White",
            result: "Blue pools in crawling texture with bare clay spots showing through",
            chemistry: "Crawling White intentionally crawls creating texture; fluid Chun pools in the recesses between crawl beads",
            bestOn: "Textural pieces, sculptural work",
            risk: "medium",
            prediction_grade: "possible",
            warning: "Crawling White behavior varies with thickness — test on similar form first",
            confidence: "medium",
            source: "Fluid over crawling glaze — predictable physics but variable outcome"
        },

        // === EARTHY / COMPLEX COMBOS ===
        {
            id: 17,
            top: "Neutral Grey",
            base: "Opaque White",
            result: "Soft grey with white breaks; lighter and cleaner than over dark bases",
            chemistry: "Opaque grey (ilmenite or manganese) over white = lighter dove grey; zirconium white prevents darkening",
            bestOn: "Subtle, elegant pieces",
            risk: "low",
            prediction_grade: "likely",
            confidence: "high",
            source: "Grey over white — straightforward"
        },
        {
            id: 18,
            top: "Chun Blue",
            base: "Panama Red",
            result: "Blue and red boundary with purple transition where glazes overlap",
            chemistry: "Both contain copper — Chun has copper+iron, Panama Red has copper+tin. Where thin, red shows through creating purple transition zone. Both copper glazes are compatible.",
            bestOn: "Pieces where color transitions are desirable",
            risk: "medium",
            prediction_grade: "possible",
            warning: "Two copper glazes may compete — test thickness ratios",
            confidence: "medium",
            source: "Copper-over-copper — less documented but chemically plausible"
        },
    ],
    user_predictions: [
        {
            id: 101,
            top: "Celadon",
            base: "Strontium Crystal Matte",
            result: "Jade green potentially obscuring crystal formations — celadon may be too opaque",
            chemistry: "Strontium Crystal forms visible crystals; celadon's translucency should allow crystals to show, but may fill texture",
            risk: "medium",
            prediction_grade: "possible",
            confidence: "low",
            warning: "Crystal glazes need specific cooling schedules — celadon over may interfere with crystal growth"
        },
        {
            id: 102,
            top: "Tenmoku",
            base: "Iron Luster",
            result: "Dark brown over golden amber — both iron-based, may lack contrast",
            chemistry: "Tenmoku (8-10% iron) over Iron Luster (4-5% iron) — both high-iron glazes stacked = risk of monotone dark brown",
            risk: "high",
            prediction_grade: "unlikely",
            confidence: "low",
            warning: "HIGH IRON WARNING: Both glazes are iron-rich. Likely results in muddy, very dark brown with no visual interest."
        },
        {
            id: 103,
            top: "Copper Red",
            base: "Tea Dust",
            result: "Likely muddy brown — copper red suppressed by Tea Dust's ~8% iron",
            chemistry: "IRON KILLS COPPER RED. Tea Dust has ~8% iron which will suppress Copper Red copper development. Expect brown/muddy result, not purple.",
            risk: "high",
            prediction_grade: "unlikely",
            confidence: "medium",
            warning: "IRON KILLS COPPER RED — this combo is likely to fail. Iron in Tea Dust will prevent copper red formation."
        },
        {
            id: 104,
            top: "Celadon",
            base: "Iron Yellow",
            result: "Green-yellow chartreuse from iron green + iron yellow combination",
            chemistry: "Both use iron as colorant — celadon has 1-2% iron (green in reduction), Iron Yellow has 4-5% iron (yellow). Combined iron shifts toward chartreuse.",
            risk: "low",
            prediction_grade: "possible",
            confidence: "medium",
            source: "Iron+iron layering — additive iron effect"
        },
        {
            id: 105,
            top: "Olive Green",
            base: "Opaque White",
            result: "Olive to forest green over white — earthier than Copper Green",
            chemistry: "Olive Green = copper green + iron (1.5% Cu + 1.5% Fe). Iron addition shifts toward olive. White base keeps it cleaner than over dark base.",
            risk: "low",
            prediction_grade: "possible",
            confidence: "medium",
            source: "Copper-iron green over white — predictable"
        },
        {
            id: 106,
            top: "Compound Black",
            base: "Opaque White",
            result: "Deep black breaking to dark brown over white; very dramatic on light clay",
            chemistry: "Compound black (Co 0.8% + Fe 3% + Mn 2%) over white = high contrast. Black breaks to brown where thin.",
            risk: "low",
            prediction_grade: "likely",
            confidence: "medium",
            source: "Dark glaze over white — high contrast approach"
        },
        {
            id: 107,
            top: "Tea Dust",
            base: "Tenmoku",
            result: "Very dark brown/black — both extremely iron-rich, likely no visual distinction",
            chemistry: "Tea Dust (~8% Fe) + Tenmoku (8-10% Fe) = massive iron overload. Expect near-black with no interesting variation.",
            risk: "high",
            prediction_grade: "unlikely",
            confidence: "low",
            warning: "HIGH IRON WARNING: Two very high-iron glazes stacked. Will be dark, muddy, and uninteresting."
        },
        {
            id: 108,
            top: "Copper Teal",
            base: "Opaque White",
            result: "Clean teal/turquoise over white — brighter and bluer than over dark base",
            chemistry: "Copper Teal is copper blue-green (1-1.5% Cu). Over white, stays bright teal. White prevents darkening.",
            risk: "low",
            prediction_grade: "likely",
            confidence: "medium",
            source: "Copper teal over white — should work well"
        },
        {
            id: 109,
            top: "Reactive Rutile",
            base: "High-Opacity White",
            result: "Reactive rutile glaze over white — color will shift based on iron in clay body and thickness",
            chemistry: "Reactive Rutile is rutile-based and reactive to iron. Over white, less iron available so expect more tan/peach with less blue/purple shift.",
            risk: "medium",
            prediction_grade: "unknown",
            confidence: "low",
            warning: "Reactive Rutile is inherently unpredictable — results vary with clay body, thickness, and firing."
        },
        {
            id: 110,
            top: "Chrome-Tin Raspberry",
            base: "Opaque White",
            result: "Deep raspberry to magenta with white breaks; needs oxidation for best pink",
            chemistry: "Chrome-tin raspberry (higher chrome than Chrome-Tin Pink) over zinc-free white. More saturated.",
            risk: "medium",
            prediction_grade: "possible",
            warning: "Chrome-tin needs oxidation. Reduction shifts toward gray. Zinc destroys the color.",
            confidence: "medium",
            source: "Same chemistry as Chrome-Tin Pink but more saturated"
        },
        {
            id: 111,
            top: "Iron-Rutile Brown",
            base: "Opaque White",
            result: "Warm brown with rutile variegation over white; cleaner than over dark base",
            chemistry: "Iron-rutile brown over white = warmer, lighter brown with visible rutile streaks",
            risk: "low",
            prediction_grade: "possible",
            confidence: "medium",
            source: "Iron-rutile over white — should maintain variegation"
        },
        {
            id: 112,
            top: "Zinc Clear",
            base: "Copper Green",
            result: "Copper green potentially intensified by zinc in clear — may shift toward turquoise",
            chemistry: "Zinc Clear contains zinc. Zinc + copper = turquoise green enhancement. Should deepen Copper Green.",
            risk: "low",
            prediction_grade: "likely",
            confidence: "medium",
            source: "Zinc enhances copper greens — documented interaction"
        },
    ],
    glazes: [
        // CLEARS - Transparent bases for layering
        {
            name: "Zinc-Free Clear",
            family: "Clears",
            hex: "#e8e4dc",
            chemistry: "Zinc-free clear glaze — silica, feldspar, whiting base",
            behavior: "Preserves true colors underneath; won't shift copper reds or chrome greens",
            layering: "Excellent over any color; protects surface without color modification. USE THIS over copper reds and chrome-tin pinks.",
            source: "Published zinc-free clear glaze formulation"
        },
        {
            name: "Zinc Clear",
            family: "Clears",
            hex: "#f0ebe3",
            chemistry: "Contains zinc oxide as flux — enhances color response from oxides",
            behavior: "Zinc enhances oxide color response; may shift chrome greens to brown; enhances copper greens toward turquoise",
            layering: "DO NOT use over chrome-tin pinks or chrome greens (zinc kills them). Good over copper greens and blues.",
            warning: "Contains zinc — destroys chrome-tin pink and shifts chrome green to brown",
            source: "Published zinc-containing clear glaze formulation"
        },

        // WHITES - Opaque white bases
        {
            name: "Opaque White",
            family: "Whites",
            hex: "#f5f2ed",
            chemistry: "Zirconium white: 8-12% zirconium silicate opacifier; zinc-free",
            behavior: "Bright opaque white; excellent coverage; reflects light through transparent overlays",
            layering: "THE base for transparent colors — ensures clean, bright development. Copper reds break white. Chrome-tin pinks NEED this (zinc-free).",
            recipe: "Custer Feldspar 40, Silica 25, Whiting 15, Kaolin 10, Zircopax 10",
            source: "Standard zirconium white — published in multiple ceramic references"
        },
        {
            name: "Crawling White",
            family: "Whites",
            hex: "#e8e2d8",
            chemistry: "Intentional crawling: High surface tension from excess magnesium + low clay + zinc",
            behavior: "Intentional crawling creates bare clay spots and glaze beads; every piece unique",
            layering: "Fluid glazes pool in crawl texture. Chun Blue creates blue pools. Celadon fills recesses with green.",
            warning: "Thickness-dependent: thin = light crawl, thick = heavy crawl. Test first.",
            recipe: "High MgO base + reduced clay content",
            source: "Community crawling white — well-known technique"
        },
        {
            name: "High-Opacity White",
            family: "Whites",
            hex: "#faf8f5",
            chemistry: "High-opacity white: 10-15% zirconium silicate opacifier; zinc-free",
            behavior: "Flat, even, very white coverage; minimal variation",
            layering: "Excellent base for all transparent colors. Ensures clean, bright color development. Zinc-free = safe for chrome-tin pinks.",
            recipe: "Custer Feldspar 40, Silica 25, Whiting 15, Kaolin 10, Zircopax 10",
            source: "Community high-opacity white — published recipe"
        },

        // NEUTRALS - Blacks and Greys
        {
            name: "Compound Black",
            family: "Neutrals",
            hex: "#1a1a1a",
            chemistry: "Compound black: Cobalt 0.8% + Iron 3% + Manganese 2%",
            behavior: "Deep true black; breaks to dark brown where thin",
            layering: "Use as accent. Dramatic over white base. Over dark bases = just more dark.",
            recipe: "Custer Feldspar 40, Silica 25, Whiting 18, Kaolin 12, EPK 5 + Cobalt Carb 0.8, Iron 3, Manganese 2",
            source: "Standard compound black — published in ceramic reference books"
        },
        {
            name: "Neutral Grey",
            family: "Neutrals",
            hex: "#6a6a6a",
            chemistry: "Neutral grey: 2-3% ilmenite (FeTiO3) OR 1-2% manganese dioxide",
            behavior: "Stable mid-grey; opaque and consistent",
            layering: "White underlayer = lighter dove grey. Over dark = grey disappears.",
            recipe: "Base glaze + Ilmenite 2.5% OR Manganese Dioxide 1.5%",
            source: "Community recipe — published in multiple references"
        },

        // GREENS - Iron-based and copper greens
        {
            name: "Copper Green",
            family: "Greens",
            hex: "#6a9a6a",
            chemistry: "Copper green: 2-3% copper carbonate; oxidation = brighter green, reduction = darker emerald",
            behavior: "Bright grass green; translucent enough to show texture",
            layering: "Over white = clean bright green. Zinc-Free Clear over = gloss without color change. Zinc Clear over = may shift toward turquoise (zinc effect).",
            recipe: "Base glaze + Copper Carbonate 2-3%",
            source: "Standard copper green — published in ceramic textbooks"
        },
        {
            name: "Olive Green",
            family: "Greens",
            hex: "#5a7a5a",
            chemistry: "Copper green + iron: 1.5% copper carbonate + 1-2% iron oxide",
            behavior: "Olive to forest green; more muted than Copper Green",
            layering: "White underlayer brightens. Iron creates brown undertones.",
            recipe: "Base glaze + Copper Carbonate 1.5%, Red Iron Oxide 1.5%",
            source: "Community copper-iron green — published recipe"
        },
        {
            name: "Jade Green",
            family: "Greens",
            hex: "#5a8a5a",
            chemistry: "Iron green: 3-5% Fe2O3 in heavy reduction; more opaque than celadon",
            behavior: "Opaque jade green; pools darker in recesses",
            layering: "Over white = brighter green. Over shino = jade over warm carbon trap.",
            recipe: "Custer Feldspar 30, Whiting 20, EPK 15, Silica 35, Red Iron Oxide 4",
            source: "Based on Ming Dynasty Chinese greenware type"
        },
        {
            name: "Celadon",
            family: "Greens",
            hex: "#7eb09b",
            chemistry: "1-2% iron oxide in reduction; calcium flux promotes jade color",
            behavior: "Translucent jade-like green; pools darker in recesses, breaks lighter on edges",
            layering: "Over shino = classic combo (jade over carbon trap). Over white = cleaner green. Over tenmoku = dark celadon.",
            recipe: "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12, Red Iron Oxide 1.5",
            source: "Traditional Asian glaze — thousands of years of history"
        },
        {
            name: "Warm Celadon",
            family: "Greens",
            hex: "#8aa07a",
            chemistry: "Warm celadon: 2-3% iron oxide + 1% yellow iron oxide; higher total iron shifts toward amber-green",
            behavior: "Warmer celadon; amber-green instead of blue-green",
            layering: "Over white = warmer green. Over shino = warm jade over carbon trap.",
            recipe: "Custer Feldspar 28, Whiting 20, EPK 20, Silica 32, Red Iron Oxide 2.5, Yellow Iron Oxide 1",
            source: "Warm celadon variation — published recipe"
        },

        // SHINOS - Carbon trap, MUST be base layer
        {
            name: "Carbon Trap Shino",
            family: "Shinos",
            hex: "#c9a070",
            chemistry: "High soda feldspar base (60-70%) with spodumene; carbon trap mechanism",
            behavior: "Iridescent metallic sheen; carbon trap orange/gray patterns",
            layering: "ACCEPTS overlays well: Tenmoku, Celadon, Iron Red work over it.",
            warning: "NEVER apply over another glaze — will crawl catastrophically. Shinos MUST be the base layer.",
            recipe: "Soda Feldspar 65, Spodumene 15, EPK 10, Nepheline Syenite 10",
            source: "Published shino formulation — well-documented in ceramic literature"
        },
        {
            name: "Classic Shino",
            family: "Shinos",
            hex: "#d4956a",
            chemistry: "High soda, low clay for maximum carbon trapping",
            behavior: "Orange/gray carbon trap patterns",
            layering: "Excellent under Celadon, Chun Blue, Tenmoku, Iron Luster.",
            warning: "NEVER apply over another glaze — will crawl. MUST be base layer.",
            recipe: "Nepheline Syenite 48, Soda Ash 4, Spodumene 22, EPK 15, Silica 11",
            source: "Published shino formulation (Malcom Davis) — widely shared"
        },

        // BLUES - Copper and cobalt blues
        {
            name: "Cobalt Blue",
            family: "Blues",
            hex: "#3a5f8a",
            chemistry: "Cobalt-based blue: 0.5-1% cobalt carbonate",
            behavior: "Stable cobalt blue; most predictable colorant",
            layering: "Over white = bright clean blue. Over iron base = blue-green/teal shift.",
            recipe: "Base glaze + Cobalt Carbonate 0.5-1%",
            source: "Standard cobalt blue — published in ceramic textbooks"
        },
        {
            name: "Copper-Cobalt Blue",
            family: "Blues",
            hex: "#4a7c9b",
            chemistry: "Copper/cobalt blend: copper 1% + cobalt 0.5%",
            behavior: "Complex blue with depth from dual colorants",
            layering: "Over white = clean complex blue. Over iron = may darken significantly.",
            source: "Community copper-cobalt blue — published recipe"
        },
        {
            name: "Chun Blue",
            family: "Blues",
            hex: "#5a8ab0",
            chemistry: "Copper (0.5-1%) + iron (1-2%) in reduction; fluid melt",
            behavior: "Blue with purple edges; creates purple flash over iron glazes like Tenmoku",
            layering: "Over Tenmoku = purple flash (classic). Over shino = blue over warm carbon trap. Over white = clean blue. Fluid — watch for runs.",
            source: "Traditional Chinese Jun/Chun ware type — published formulation"
        },
        {
            name: "Copper Teal",
            family: "Blues",
            hex: "#4a8a7a",
            chemistry: "Copper blue-green (teal): 1-1.5% copper carbonate; atmosphere determines blue vs green",
            behavior: "Teal to blue-green; oxidation = greener, reduction = bluer",
            layering: "Over white = brighter teal. Clear over adds gloss.",
            recipe: "Base glaze + Copper Carbonate 1.2%",
            source: "Community copper teal — published recipe"
        },

        // REDS - Copper reds and iron reds
        {
            name: "Iron Red",
            family: "Reds",
            hex: "#8b3a3a",
            chemistry: "Iron saturation red: 8-12% iron oxide in reduction",
            behavior: "Deep rust red to brick red; breaks to amber where thin",
            layering: "Over shino = warm metallic-red. Over white = cleaner red. NOT compatible with copper reds (both compete).",
            recipe: "Custer Feldspar 40, Whiting 15, EPK 15, Silica 30, Red Iron Oxide 10",
            source: "Classic iron red glaze — published in ceramic references"
        },
        {
            name: "Copper Red",
            family: "Reds",
            hex: "#b33a3a",
            chemistry: "Copper red: 0.5-1.5% CuCO3 in heavy reduction with tin oxide 1-2%",
            behavior: "Bright copper red; requires heavy reduction starting at cone 012; breaks to white on edges over white base",
            layering: "Zinc-Free Clear over preserves red. Zinc Clear over RISKS shifting red (has zinc). Over white = clean breaks. Iron in base KILLS this glaze.",
            warning: "NEVER layer over iron-rich bases. Iron suppresses copper red development.",
            recipe: "Potash Feldspar 40, Whiting 20, Kaolin 15, Silica 25 + Tin Oxide 1.5%, Copper Carbonate 0.75%",
            source: "Published in John Britt — The Complete Guide to High-Fire Glazes"
        },
        {
            name: "Panama Red",
            family: "Reds",
            hex: "#a83232",
            chemistry: "Copper red: 0.5-1% CuCO3 + 1-2% tin oxide in reduction",
            behavior: "Blood red to tomato red; may show blue-purple edges where thin over white",
            layering: "Zinc-Free Clear over preserves red. Opaque White under = clean breaks. Iron in base KILLS this glaze.",
            warning: "Requires heavy reduction. Iron kills copper red. Zinc-containing clears may shift color.",
            recipe: "Custer Feldspar 48, Whiting 14, EPK 6, Silica 15, Ferro 3134 9, Zinc 0.5, Talc 4 + Tin 1.2%, Copper Carbonate 0.8%",
            source: "Published in John Britt — Panama Red family"
        },

        // PURPLES - Manganese and cobalt purples
        {
            name: "Manganese Purple",
            family: "Purples",
            hex: "#7a4a8a",
            chemistry: "Manganese-cobalt purple: 3-4% manganese dioxide + 0.5% cobalt carbonate",
            behavior: "Vibrant purple; surface depends on base glaze",
            layering: "Zinc-Free Clear over adds gloss. White underlayer = brighter lavender.",
            recipe: "Base glaze + Manganese Dioxide 3.5%, Cobalt Carbonate 0.5%",
            source: "Community manganese-cobalt purple — published recipe"
        },
        {
            name: "Chrome-Tin Pink",
            family: "Purples",
            hex: "#c9a0b0",
            chemistry: "Chrome-tin pink: Chrome oxide 0.2-0.4% + tin oxide 1.5-2%",
            behavior: "Soft coral to rose pink",
            layering: "White underlayer ESSENTIAL (prevents muddy result). MUST use zinc-free clear over. Zinc destroys this color.",
            warning: "Zinc destroys chrome-tin pink. Needs oxidation for best color. Reduction may shift toward gray-green.",
            recipe: "Base + Chrome Oxide 0.3%, Tin Oxide 1.5%",
            source: "Chrome-tin pink — published in ceramic chemistry references"
        },
        {
            name: "Chrome-Tin Raspberry",
            family: "Purples",
            hex: "#a04060",
            chemistry: "Chrome-tin raspberry: higher chrome (0.4-0.5%) + tin oxide (2%)",
            behavior: "Deep raspberry to magenta; more saturated than Chrome-Tin Pink",
            layering: "White underlayer essential. Zinc-free clear only.",
            warning: "Same zinc/oxidation warnings as Chrome-Tin Pink. Higher chrome = more saturated but less forgiving.",
            recipe: "Base + Chrome Oxide 0.4%, Tin Oxide 2%",
            source: "Chrome-tin raspberry — published in ceramic chemistry references"
        },

        // BROWNS - High iron darks
        {
            name: "Iron-Rutile Brown",
            family: "Browns",
            hex: "#5a4030",
            chemistry: "Iron-rutile brown: 5-6% red iron oxide + 2-3% rutile",
            behavior: "Rich warm brown with rutile variegation",
            layering: "Accepts transparent overlays. Celadon over = olive-brown. Chun over = brown with blue edges.",
            recipe: "Custer Feldspar 40, Whiting 15, EPK 10, Silica 35, Red Iron Oxide 5, Rutile 3",
            source: "Community iron-rutile brown — published recipe"
        },
        {
            name: "Tea Dust",
            family: "Browns",
            hex: "#6a5540",
            chemistry: "High iron (~8%) + rutile/ilmenite for crystal spots",
            behavior: "Dark brown with yellow-green crystal spots",
            layering: "Very iron-rich — will darken any glaze over it. DO NOT combine with copper reds (iron kills them).",
            warning: "Very high iron content. Will suppress copper red development if layered under copper reds.",
            source: "Traditional tea dust glaze — published in ceramic reference books"
        },
        {
            name: "Tenmoku",
            family: "Browns",
            hex: "#2a1a10",
            chemistry: "8-10% iron oxide in reduction; stiff melt",
            behavior: "Dark brown/black with amber breaks where thin",
            layering: "Chun Blue over = purple flash at boundary. Celadon over = dark celadon. Very iron-rich — dominates overlying glazes.",
            recipe: "Custer Feldspar 35, Silica 25, Whiting 15, Kaolin 15, Iron Oxide 10",
            source: "Traditional Japanese glaze — centuries of history"
        },
        {
            name: "Rutile-Eye Brown",
            family: "Browns",
            hex: "#3a2a1a",
            chemistry: "Iron oxide (5%) + Rutile (4%) — rutile creates 'eye' variegation",
            behavior: "Dark brown/black with variegated 'eye' patterns from rutile",
            layering: "Similar to Tenmoku behavior. Accepts transparent overlays.",
            recipe: "Custer Feldspar 40, Whiting 20, EPK 10, Silica 30, Red Iron Oxide 5, Rutile 4",
            source: "Published on Ceramic Action blog (Matt Fiske)"
        },

        // YELLOWS - Iron and praseodymium yellows
        {
            name: "Iron Yellow",
            family: "Yellows",
            hex: "#c9a962",
            chemistry: "Iron yellow: 4-5% yellow iron oxide (FeOOH) or praseodymium zirconium stain",
            behavior: "Warm honey yellow; varies with atmosphere",
            layering: "Celadon over = chartreuse (iron+iron). Chun Blue over = blue where they meet.",
            recipe: "Iron: Base + Yellow Iron Oxide 4% OR Praseodymium Stain 6%",
            source: "Community iron yellow — published recipe"
        },
        {
            name: "Iron Luster",
            family: "Yellows",
            hex: "#c9a050",
            chemistry: "Iron reduction luster: 4-5% iron oxide with slow cooling",
            behavior: "Golden honey to amber; iridescent from iron crystallization",
            layering: "Tenmoku over = dramatic dark-over-gold. Zinc-Free Clear over = gloss without shift.",
            recipe: "Base glaze + Red Iron Oxide 4.5%",
            source: "Community iron luster — published recipe"
        },

        // CRYSTALS
        {
            name: "Strontium Crystal Matte",
            family: "Crystals",
            hex: "#a09080",
            chemistry: "High strontium carbonate as flux — creates macro-crystalline matte surface",
            behavior: "Forms visible crystal structures; matte base",
            layering: "Celadon over may obscure crystals. Clear over adds gloss.",
            recipe: "Strontium Carbonate 18, Feldspar 35, Silica 30, Kaolin 15, Whiting 2",
            source: "Pete Pinnell Strontium Crystal Matte — published on Glazy.org"
        },

        // REACTIVE
        {
            name: "Reactive Rutile",
            family: "Reactive",
            hex: "#7a6a5a",
            chemistry: "Rutile-based (TiO2 with ~10% iron); reactive to iron in clay body",
            behavior: "Highly variegating: tan/peach when thick, blue/purple near iron",
            layering: "Unpredictable. Color responds to iron content in clay body and thickness.",
            source: "Community rutile-based reactive glaze — published formulation"
        }
    ],
    ideas: []
};

// Export for use
window.DATA = DATA;
window.FAMILY_ORDER = FAMILY_ORDER;
window.COLORANT_RULES = COLORANT_RULES;
