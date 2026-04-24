/**
 * GlazeTips - Quick reference for glaze fundamentals
 * Covers UMF, food safety, common defects, firing basics
 */
class GlazeTips {
    constructor(container) {
        this.container = container;
        this.element = null;
        this.render();
    }

    render() {
        this.element = document.createElement('div');
        this.element.className = 'glaze-tips';
        this.container.appendChild(this.element);
    }

    show() {
        this.element.style.display = 'block';
        this.element.innerHTML = this._buildHTML();
        this._attachEvents();
    }

    hide() {
        this.element.style.display = 'none';
    }

    _buildHTML() {
        return `
        <div class="tips-header">
            <h1>Glaze Fundamentals</h1>
            <p class="tips-subtitle">Quick reference for anyone getting started with glazes and glaze chemistry</p>
        </div>

        ${this._tipCard('umf', 'Unity Molecular Formula (UMF)',
            `The UMF is a standardized way of writing glaze chemistry as molecular ratios.
            All fluxes (the melting oxides) are normalized so they add up to <strong>1.0</strong>.
            Once you know the UMF, you can predict <em>tendencies</em> &mdash; whether a glaze is likely to be glossy or matte, runny or stable &mdash; before you fire it.`,
            `<div class="tips-example">
                <strong>Reading a UMF:</strong><br>
                <code>K2O 0.29 &middot; Na2O 0.13 &middot; CaO 0.58</code> &mdash; the fluxes (sum = 1.0)<br>
                <code>Al2O3 0.69</code> &mdash; the stabilizer<br>
                <code>SiO2 5.83</code> &mdash; the glass former
            </div>
            <div class="tips-box tips-box-blue">
                <strong>The SiO2:Al2O3 ratio is the single most useful number in glaze chemistry.</strong>
                <ul>
                    <li>Below 1.5:1 &mdash; tends to be dry, may be underfired</li>
                    <li>1.5:1 to 4:1 &mdash; matte to satin surface</li>
                    <li>4:1 to 7:1 &mdash; satin to glossy surface</li>
                    <li>7:1 to 10:1 &mdash; tends toward glossy surface</li>
                    <li>Above 10:1 &mdash; high gloss; increased risk of running</li>
                </ul>
            </div>
            <p>UMF lets you compare two completely different recipes and see they're actually the same glaze, or understand why one runs and the other doesn't. Tools like <strong>Glazy.org</strong> calculate UMF automatically from recipes.</p>`
        )}

        ${this._tipCard('food-safety', 'Food Safety',
            `A glaze is "food safe" when it won't leach harmful materials into food or drink.
            This depends on <strong>two things</strong>: the chemistry (no toxic oxides in soluble form)
            and the surface (intact, uncracked, fully melted).`,
            `<div class="tips-box tips-box-green">
                <strong>What makes a glaze food safe:</strong>
                <ul>
                    <li>No lead, barium, or cadmium in leachable amounts</li>
                    <li>Fully melted, smooth, glossy surface (no crawling, pinholing, or rough texture)</li>
                    <li>No crazing (cracks can trap bacteria)</li>
                    <li>Fired to maturity (underfired glazes leach more)</li>
                </ul>
            </div>
            <div class="tips-box tips-box-red">
                <strong>What makes a glaze NOT food safe:</strong>
                <ul>
                    <li>Cracked, crazed, or crawled surfaces &mdash; even safe chemistry becomes unsafe if the surface is broken</li>
                    <li>High barium or copper &mdash; these can leach, especially with acidic food</li>
                    <li>Matte surfaces &mdash; tend to release oxides more readily than glossy surfaces</li>
                    <li>Underfired glazes &mdash; not fully melted, more porous</li>
                </ul>
            </div>
            <p><strong>The acid test:</strong> squeeze fresh lemon juice onto a glazed surface and leave it for 24 hours. If the glaze changes color or the juice tastes metallic, it's not food safe. This is the simplest at-home test.</p>
            <p><strong>Food safety is combinational</strong> &mdash; safe chemistry + intact surface + proper firing. One weak link breaks the chain. Matte surfaces from <strong>underfiring</strong> are the primary leaching risk. True matte glazes (high alumina, fully fired) can be food safe.</p>
            <p>Note: a manufacturer's "food safe" label applies to <em>their specific firing conditions</em>. The same glaze underfired by a cone may not be safe.</p>`
        )}

        ${this._tipCard('crawling', 'Crawling',
            `Crawling is when the glaze pulls away from the clay body during firing, leaving bare patches
            of exposed clay. It's one of the most common glaze defects.`,
            `<div class="tips-box">
                <strong>Why it happens:</strong>
                <ul>
                    <li><strong>Dust, oil, or lint</strong> on the bisque surface &mdash; wipe with a damp sponge before glazing</li>
                    <li><strong>Applied too thick</strong> &mdash; especially with high-clay-content glazes like Shino</li>
                    <li><strong>Incompatible chemistry</strong> &mdash; Shino over a non-Shino glaze is a classic example</li>
                    <li><strong>High shrinkage</strong> &mdash; some raw clay materials shrink a lot as they dry, pulling the glaze apart</li>
                    <li><strong>Overfiring</strong> &mdash; the glaze becomes so fluid it dewets the surface</li>
                </ul>
            </div>
            <p>Crawling isn't always a defect. Some potters intentionally create crawl textures as a surface quality. If that's what you want, apply the glaze thick over a dusty or slightly oily surface, and fire to the upper end of the glaze's range.</p>`
        )}

        ${this._tipCard('running', 'Running',
            `Running (or "flowing") is when a glaze becomes too fluid during firing and drips down the piece.
            It can ruin kiln shelves and stick pots together.`,
            `<div class="tips-box">
                <strong>Why it happens:</strong>
                <ul>
                    <li><strong>Too much flux</strong> relative to silica and alumina</li>
                    <li><strong>Overfiring</strong> &mdash; even a well-balanced glaze will run if fired too hot</li>
                    <li><strong>Applied too thick</strong> &mdash; more glaze = more mass = more flow</li>
                    <li><strong>Thin walls</strong> &mdash; less clay to absorb the melt, glaze runs farther</li>
                </ul>
            </div>
            <p>Check the UMF: if SiO2:Al2O3 is above 10:1 or flux:Al2O3 is above 3:1, the glaze is likely to run. Always use kiln wash, wadding, or a setter under pieces with runny glazes.</p>
            <p>Like crawling, running can be intentional. Many potters use running glazes for layered, flowing effects on vertical surfaces.</p>`
        )}

        ${this._tipCard('crazing', 'Crazing',
            `Crazing is a network of fine cracks in the glaze surface. It happens when the glaze
            and clay body cool at different rates &mdash; a thermal expansion mismatch.`,
            `<div class="tips-box">
                <strong>The science:</strong> glazes contract slightly as they cool. If the glaze contracts more than the clay beneath it, it cracks to relieve the tension. This is measured as the <strong>Coefficient of Thermal Expansion (COE)</strong>.
            </div>
            <div class="tips-box tips-box-blue">
                <strong>Common causes:</strong>
                <ul>
                    <li><strong>High silica or high alkali</strong> (K2O, Na2O) in the glaze &mdash; both increase thermal expansion</li>
                    <li><strong>Fast cooling</strong> &mdash; thermal shock stresses the glaze</li>
                    <li><strong>Glaze too thin</strong> &mdash; less able to absorb stress</li>
                    <li><strong>Clay body too porous</strong> &mdash; can't "grip" the glaze well enough</li>
                </ul>
            </div>
            <p><strong>Fixing crazing:</strong> increase silica, decrease feldspar (alkali source), add silica to the body, or slow the cooling. The UMF tells you if your glaze is expansion-heavy.</p>
            <p>Crazing is a food safety concern because bacteria can live in the cracks. It's also a structural weakness &mdash; crazed ware is less durable over time.</p>`
        )}

        ${this._tipCard('atmosphere', 'Oxidation vs Reduction',
            `The kiln atmosphere during firing dramatically changes glaze colors and surfaces.
            This is one of the most powerful variables in ceramics.`,
            `<div class="tips-columns">
                <div class="tips-column">
                    <strong>Oxidation</strong> (plenty of oxygen)
                    <ul>
                        <li>Electric kilns (always oxidation)</li>
                        <li>Gas kiln with damper open</li>
                        <li>Clean, predictable colors</li>
                        <li>Iron = amber, brown, tan</li>
                        <li>Copper = green, turquoise</li>
                    </ul>
                </div>
                <div class="tips-column">
                    <strong>Reduction</strong> (oxygen-starved)
                    <ul>
                        <li>Gas kiln with damper closed</li>
                        <li>Carbon-rich atmosphere strips oxygen from glaze</li>
                        <li>More dramatic, less predictable</li>
                        <li>Iron = celadon green, blue-gray, tenmoku black</li>
                        <li>Copper = copper red, luster, sometimes metallic</li>
                    </ul>
                </div>
            </div>
            <p>The same exact glaze recipe can look completely different depending on atmosphere. A glaze tested in oxidation (electric kiln) may behave nothing like you expect in reduction (gas kiln).</p>
            <p><strong>Heavy reduction</strong> (lots of carbon introduced) pushes color changes further. Copper reds only develop in heavy reduction. But heavy reduction also makes results less predictable.</p>`
        )}

        ${this._tipCard('layering', 'Layering Glazes',
            `When you layer glazes, the order matters enormously. "A OVER B" means A is the
            <strong>top layer</strong> (applied last) and B is the <strong>base layer</strong> (applied first).
            The top glaze interacts with the base glaze during firing.`,
            `<div class="tips-box tips-box-blue">
                <strong>General rules:</strong>
                <ul>
                    <li><strong>Similar chemistry = compatible.</strong> Two cone 10 stoneware glazes with similar flux profiles will usually layer fine.</li>
                    <li><strong>Different chemistry = unpredictable.</strong> A low-fire glaze over a high-fire glaze, or a Shino over a glossy base, can crawl, bubble, or produce unexpected colors.</li>
                    <li><strong>The top glaze dominates the surface.</strong> Its color and texture are what you see most.</li>
                    <li><strong>The base glaze affects the interaction.</strong> Iron in the base can bleed through the top glaze, changing its color.</li>
                </ul>
            </div>
            <div class="tips-box">
                <strong>Shino layering rules (important):</strong>
                <ul>
                    <li>Shino OVER Shino &mdash; fine (same chemistry)</li>
                    <li>Shino OVER non-Shino &mdash; high crawl risk (Shinos shrink significantly during drying and firing)</li>
                    <li>Non-Shino OVER Shino &mdash; usually works (Shino makes a good base)</li>
                </ul>
            </div>
            <p>Always test first. Make small test tiles before committing to a full piece. Layering is where the most surprising (and sometimes most beautiful) results happen.</p>`
        )}

        ${this._tipCard('cones', 'Cone Temperatures',
            `Orton cones measure <strong>heatwork</strong> &mdash; the combination of temperature and time.
            A cone doesn't just measure degrees; it measures how much heat the glaze has absorbed.
            This is why a "slow" cone 10 firing reaches a lower peak temperature than a "fast" one.`,
            `<div class="tips-box">
                <strong>Common cone ranges:</strong>
                <ul>
                    <li><strong>Cone 06</strong> (~993&deg;C / 1820&deg;F) &mdash; low-fire, earthenware</li>
                    <li><strong>Cone 6</strong> (~1222&deg;C / 2232&deg;F) &mdash; mid-range, most common in electric kilns</li>
                    <li><strong>Cone 10</strong> (~1285&deg;C / 2345&deg;F) &mdash; high-fire, stoneware and porcelain</li>
                </ul>
            </div>
            <p>A glaze designed for cone 10 won't melt properly at cone 6 (underfired, rough, dry). A cone 6 glaze fired to cone 10 may run off the piece entirely (overfired, too fluid).</p>
            <p>The UMF target formulas in OpenGlaze are primarily calibrated for stoneware temperatures. Limits shift for different cones and atmospheres &mdash; these are guidelines, not absolute rules.</p>`
        )}

        ${this._tipCard('iron-copper', 'Iron & Copper Behavior',
            `Iron and copper are the two most common colorants in ceramics, and both are
            dramatically affected by firing atmosphere and concentration.`,
            `<div class="tips-columns">
                <div class="tips-column">
                    <strong>Iron Oxide</strong>
                    <ul>
                        <li>0.5% in reduction &mdash; pale celadon</li>
                        <li>1-2% in reduction &mdash; classic celadon green</li>
                        <li>2-4% in oxidation &mdash; amber, tan, honey</li>
                        <li>5-8% in reduction &mdash; tenmoku (dark brown/black)</li>
                        <li>8%+ in reduction &mdash; iron saturated, can produce iron spots and "oil spot" effects</li>
                    </ul>
                </div>
                <div class="tips-column">
                    <strong>Copper Oxide / Carbonate</strong>
                    <ul>
                        <li>0.25% in reduction &mdash; pale blush pink</li>
                        <li>0.5-1% in reduction &mdash; copper red</li>
                        <li>1-2% in oxidation &mdash; green, turquoise</li>
                        <li>2%+ in oxidation &mdash; deep green</li>
                        <li>Any amount, heavy reduction &mdash; metallic luster, sometimes purple</li>
                    </ul>
                </div>
            </div>
            <p><strong>Key point:</strong> the same amount of iron or copper produces completely different colors depending on atmosphere. A glaze that's green in your electric kiln could be red in a gas kiln. Always note the firing conditions.</p>
            <p><strong>Base glaze chemistry matters hugely.</strong> Color depends heavily on the base glaze, not just percentage and atmosphere. Ca-heavy bases push iron toward celadon/yellow-green; K-heavy bases allow deeper greens. Copper reds require low-alumina, high-silica bases.</p>
            <p>Both iron and copper are <strong>fluxes</strong> &mdash; they don't just add color, they also melt the glaze. High amounts will make the glaze runnier.</p>`
        )}

        ${this._tipCard('troubleshooting', 'Quick Troubleshooting',
            `When a glaze doesn't behave as expected, the UMF usually explains why.
            Here are the most common problems and their chemical causes.`,
            `<div class="tips-table-wrap">
                <table class="tips-table">
                    <thead>
                        <tr><th>Problem</th><th>Likely Cause in UMF</th><th>Fix</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Crazing</td>
                            <td>High KNaO (alkali) relative to silica, or glaze COE too high for clay body</td>
                            <td>Increase silica, reduce feldspar (alkali source)</td>
                        </tr>
                        <tr>
                            <td>Running</td>
                            <td>SiO2:Al2O3 above 10, or flux:Al2O3 above 3</td>
                            <td>Increase alumina, reduce flux</td>
                        </tr>
                        <tr>
                            <td>Matte when you want glossy</td>
                            <td>Al2O3 above 0.4</td>
                            <td>Substitute some kaolin for silica</td>
                        </tr>
                        <tr>
                            <td>Glossy when you want matte</td>
                            <td>SiO2:Al2O3 above 5, low Al2O3</td>
                            <td>Add kaolin or increase Al2O3 source</td>
                        </tr>
                        <tr>
                            <td>Crawling</td>
                            <td>Low Al2O3, high surface tension; high clay content (especially Shinos); poor bisque prep (dust/oil)</td>
                            <td>Add EPK/clay, reduce boron; wipe bisque with damp sponge; thinner coats on Shinos</td>
                        </tr>
                        <tr>
                            <td>Pinholing</td>
                            <td>Underfired, or too stiff a melt</td>
                            <td>Adjust flux, verify cone reached</td>
                        </tr>
                        <tr>
                            <td>Shivering (flaking off)</td>
                            <td>Glaze COE too low for clay body</td>
                            <td>Increase flux, decrease silica</td>
                        </tr>
                    </tbody>
                </table>
            </div>`
        )}
        `;
    }

    _tipCard(id, title, intro, details) {
        return `
        <div class="tip-card" id="tip-${id}">
            <div class="tip-card-header">
                <h2>${title}</h2>
                <button class="tip-toggle" aria-expanded="true" aria-controls="tip-body-${id}">&minus;</button>
            </div>
            <div class="tip-card-body" id="tip-body-${id}">
                <p class="tip-intro">${intro}</p>
                ${details}
            </div>
        </div>`;
    }

    _attachEvents() {
        this.element.querySelectorAll('.tip-toggle').forEach(btn => {
            btn.addEventListener('click', () => {
                const card = btn.closest('.tip-card');
                const body = card.querySelector('.tip-card-body');
                const isOpen = body.style.display !== 'none';
                body.style.display = isOpen ? 'none' : 'block';
                btn.textContent = isOpen ? '+' : '\u2212';
                btn.setAttribute('aria-expanded', !isOpen);
            });
        });
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

window.GlazeTips = GlazeTips;
