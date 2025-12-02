class IsomorphismVisualizer {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.selectedNode = null;
        this.selectedArc = null;
    }

    render() {
        if (!this.container) {
            console.error(`Container ${this.container} not found`);
            return;
        }

        this.container.innerHTML = this.data.visualization_svg;
        this.setupInteractions();
    }

    setupInteractions() {
        this.setupNodeHovers();
        this.setupArcHovers();
    }

    setupNodeHovers() {
        const nodes = this.container.querySelectorAll('[data-node-id]');
        nodes.forEach(node => {
            node.addEventListener('mouseenter', (e) => {
                const nodeId = e.currentTarget.dataset.nodeId;
                this.highlightConnectedArcs(nodeId);
            });

            node.addEventListener('mouseleave', () => {
                this.unhighlightArcs();
            });

            node.addEventListener('click', (e) => {
                e.preventDefault();
                this.expandNodeDetail(nodeId);
            });
        });
    }

    setupArcHovers() {
        const arcs = this.container.querySelectorAll('[data-morphism-id]');
        arcs.forEach(arc => {
            arc.addEventListener('mouseenter', (e) => {
                const morphismId = e.currentTarget.dataset.morphismId;
                const morphismType = e.currentTarget.dataset.morphismType;
                const strength = e.currentTarget.dataset.strength;

                const parentGroup = e.currentTarget.closest('[data-morphism-id]');
                if (parentGroup) {
                    const line = parentGroup.querySelector('.morphism-line');
                    if (line) {
                        line.style.strokeWidth = '5';
                        line.style.opacity = '1';
                    }
                }
            });

            arc.addEventListener('mouseleave', (e) => {
                const parentGroup = e.currentTarget.closest('[data-morphism-id]');
                if (parentGroup) {
                    const line = parentGroup.querySelector('.morphism-line');
                    if (line) {
                        line.style.strokeWidth = null;
                        line.style.opacity = null;
                    }
                }
            });

            arc.addEventListener('click', (e) => {
                e.preventDefault();
                const morphismId = e.currentTarget.dataset.morphismId;
                this.expandMorphismDetail(morphismId);
            });
        });
    }

    highlightConnectedArcs(nodeId) {
        const arcs = this.container.querySelectorAll('[data-morphism-id]');
        arcs.forEach(arc => {
            const sourceMatch = nodeId.includes('left');
            const targetMatch = nodeId.includes('right');

            if ((sourceMatch && arc.getAttribute('data-morphism-type')) ||
                (targetMatch && arc.getAttribute('data-morphism-type'))) {
                arc.style.opacity = '1';
            } else {
                arc.style.opacity = '0.3';
            }
        });
    }

    unhighlightArcs() {
        const arcs = this.container.querySelectorAll('[data-morphism-id]');
        arcs.forEach(arc => {
            arc.style.opacity = null;
        });
    }

    expandNodeDetail(nodeId) {
        const detailPanel = document.getElementById('morphism-detail-panel');
        if (!detailPanel) {
            console.warn('Detail panel not found');
            return;
        }

        const component = this.extractComponentFromNodeId(nodeId);
        const systemData = nodeId.includes('left') ? this.data.system1 : this.data.system2;

        let content = `
            <div class="detail-section">
                <h3>${component.label}</h3>
                <div class="detail-content">
                    <p><strong>Symbol:</strong> <code>${component.symbol}</code></p>
                    <p><strong>Description:</strong> ${component.description}</p>
                    <p><strong>Domain:</strong> ${component.domain || 'N/A'}</p>
                    <p><strong>Units:</strong> ${component.units || 'N/A'}</p>
                </div>
            </div>
        `;

        detailPanel.innerHTML = content;
        detailPanel.classList.remove('hidden');
    }

    expandMorphismDetail(morphismId) {
        const detailPanel = document.getElementById('morphism-detail-panel');
        if (!detailPanel) return;

        const morphism = this.data.morphisms.find(m => m.id === morphismId);
        if (!morphism) return;

        const strengthColor = this.getStrengthColor(morphism.strength);

        let content = `
            <div class="morphism-detail-section">
                <h4>${morphism.source} → ${morphism.target}</h4>
                <div class="morphism-badge" style="background-color: ${strengthColor}; color: white; padding: 8px; border-radius: 4px; margin: 10px 0;">
                    <strong>${morphism.morphism_type}</strong> (${(morphism.strength * 100).toFixed(1)}%)
                </div>
                <div class="morphism-text">
                    <strong>Justification:</strong>
                    <p>${morphism.justification}</p>
                </div>
        `;

        if (morphism.analysis_points && morphism.analysis_points.length > 0) {
            content += `
                <div class="morphism-text">
                    <strong>Analysis Points:</strong>
                    <ul>
                        ${morphism.analysis_points.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (morphism.parameter_map && Object.keys(morphism.parameter_map).length > 0) {
            content += `
                <div class="parameter-mapping">
                    <strong>Parameter Correspondence:</strong>
                    <table>
                        ${Object.entries(morphism.parameter_map).map(([k, v]) => 
                            `<tr><td>${k}</td><td>↔</td><td>${v}</td></tr>`
                        ).join('')}
                    </table>
                </div>
            `;
        }

        if (morphism.information_loss) {
            content += `
                <div class="warning-box" style="background-color: #fee; padding: 8px; border-radius: 4px; margin-top: 10px;">
                    <strong>⚠️ Information Loss:</strong>
                    <p>${morphism.information_loss}</p>
                </div>
            `;
        }

        content += '</div>';
        detailPanel.innerHTML = content;
        detailPanel.classList.remove('hidden');
    }

    extractComponentFromNodeId(nodeId) {
        const parts = nodeId.split('_');
        const position = parts[0];
        const componentType = parts[1];

        const systemData = position === 'left' ? this.data.system1 : this.data.system2;

        const componentMap = {
            'Input': systemData.input,
            'Output': systemData.output,
            'State': systemData.state_variables,
            'StateFn': systemData.next_state_function,
            'TransFn': systemData.transfer_function,
            'Interface': systemData.interface
        };

        const component = componentMap[componentType] || {};
        return {
            label: componentType,
            symbol: component.symbol || component.symbols ? component.symbols[0] : componentType,
            description: component.description || '',
            domain: component.domain || '',
            units: component.units || ''
        };
    }

    getStrengthColor(strength) {
        if (strength >= 0.8) return '#22C55E';
        if (strength >= 0.5) return '#EAB308';
        return '#EF4444';
    }
}

function initializeIsomorphismVisualization(data) {
    const visualizer = new IsomorphismVisualizer('morphism-svg-canvas', data);
    visualizer.render();

    const analysisReport = document.getElementById('morphism-analysis-report');
    if (analysisReport && data.statistics) {
        const stats = data.statistics;
        analysisReport.innerHTML = `
            <div class="analysis-report">
                <h3>Isomorphism Analysis Summary</h3>
                <div class="statistics-grid">
                    <div class="stat-item">
                        <span class="stat-label">Total Morphisms:</span>
                        <span class="stat-value">${stats.total_morphisms}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Isomorphic:</span>
                        <span class="stat-value" style="color: #22C55E;">${stats.isomorphic_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Homomorphic:</span>
                        <span class="stat-value" style="color: #EAB308;">${stats.homomorphic_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Avg Strength:</span>
                        <span class="stat-value">${(stats.average_strength * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    }
}
