document.addEventListener('DOMContentLoaded', () => {
    // API Configuration
    const API_BASE_URL = window.location.origin; // Adapts to current host

    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const projectSection = document.getElementById('project-section');
    const resultsSection = document.getElementById('results-section');
    const goToResultsBtn = document.getElementById('go-to-results');
    const backToProjectBtn = document.getElementById('back-to-project');
    const apiStatus = document.getElementById('api-status');
    const refreshBtn = document.getElementById('refresh-btn');

    // --- Sidebar Toggle Logic ---
    // Add backdrop logic
    const backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);

    function toggleSidebar() {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            sidebar.classList.toggle('mobile-open');
            sidebarToggle.classList.toggle('shifted'); // If we want to animate icon
            backdrop.classList.toggle('active');

            // Toggle icon text?
            sidebarToggle.textContent = sidebar.classList.contains('mobile-open') ? '✕' : '☰';
        } else {
            sidebar.classList.toggle('collapsed');
        }

        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    }

    sidebarToggle.addEventListener('click', toggleSidebar);
    backdrop.addEventListener('click', () => {
        // Close on backdrop click
        if (sidebar.classList.contains('mobile-open')) {
            toggleSidebar();
        }
    });

    // Handle resize to reset states if switching modes
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
            backdrop.classList.remove('active');
            sidebarToggle.textContent = '☰';
        }
    });

    // --- Navigation Logic ---
    goToResultsBtn.addEventListener('click', () => {
        // Hide only the 2-column grid content (About/Stack/Process)
        const gridContent = projectSection.querySelector('.two-column-grid');
        if (gridContent) {
            gridContent.style.display = 'none';
        }

        // Setup Loading Section
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection.parentElement !== projectSection) {
            projectSection.appendChild(loadingSection);
        }
        const loadingText = loadingSection.querySelector('h2');
        loadingSection.classList.remove('hidden');

        // Setup Results Section (Show immediately, but hide children)
        resultsSection.classList.remove('hidden');
        resultsSection.classList.add('active');

        // Hide specific elements initially
        const backBtn = document.getElementById('back-to-project');
        if (backBtn) backBtn.style.opacity = '0';

        const resultSections = resultsSection.querySelectorAll('.results-grid > section');
        resultSections.forEach(section => {
            section.style.opacity = '0';
            section.style.transition = 'opacity 1s ease';
            section.style.display = 'block';
        });

        // Trigger resize for charts
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 50);

        // Dynamic Loading Text Sequence
        const messages = [
            "Connecting to Database...",
            "Fetching Logistics Data...",
            "Analyzing Delivery Routes...",
            "Calculating Delay Metrics...",
            "Correlating Weight vs. Time...",
            "Generating Visualizations...",
            "Finalizing Report..."
        ];

        let step = 0;
        loadingText.textContent = messages[0];

        const interval = setInterval(() => {
            step++;
            if (step < messages.length) {
                loadingText.textContent = messages[step];
            }

            // Progressive Reveal Logic
            if (step === 2 && resultSections[0]) {
                resultSections[0].style.opacity = '1';
                resultSections[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            if (step === 4 && resultSections[1]) {
                resultSections[1].style.opacity = '1';
                resultSections[1].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            if (step === 6) {
                if (resultSections[2]) resultSections[2].style.opacity = '1';
                if (resultSections[3]) resultSections[3].style.opacity = '1';
                // Scroll to the last visible part
                if (resultSections[2]) resultSections[2].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

        }, 1000);

        // End of Loading (7 seconds)
        setTimeout(() => {
            clearInterval(interval);
            loadingSection.classList.add('hidden');

            // Hide Project Section (Start Button)
            projectSection.classList.remove('active');
            projectSection.classList.add('hidden');

            // Show Back Button
            if (backBtn) {
                backBtn.style.opacity = '1';
                backBtn.style.transition = 'opacity 0.5s ease';
            }

            // Ensure all sections are visible
            resultSections.forEach(section => {
                section.style.opacity = '1';
            });

        }, 7000);
    });

    if (backToProjectBtn) {
        backToProjectBtn.addEventListener('click', () => {
            resultsSection.classList.remove('active');
            resultsSection.classList.add('hidden');
            projectSection.classList.remove('hidden');
            projectSection.classList.add('active');

            // Restore Grid Content
            const gridContent = projectSection.querySelector('.two-column-grid');
            if (gridContent) {
                gridContent.style.display = '';
            }

            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --- API & Data Logic ---

    async function checkApiStatus() {
        const indicator = apiStatus.querySelector('.status-indicator');
        indicator.textContent = 'Checking...';
        indicator.className = 'status-indicator';

        try {
            // Using Promise.race to enforce timeout
            const timeout = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Timeout')), 3000)
            );

            const request = fetch(`${API_BASE_URL}/api/rating`);
            const response = await Promise.race([request, timeout]);

            if (response.ok) {
                indicator.textContent = '● API Connected';
                indicator.classList.add('status-green');
            } else {
                indicator.textContent = '○ API Issue';
                indicator.classList.add('status-orange');
            }
        } catch (error) {
            indicator.textContent = '○ API Offline';
            indicator.classList.add('status-red');
            console.error('API Check Failed:', error);
        }
    }

    async function fetchAndRenderData() {
        try {
            const [ratingRes, corelRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/rating`),
                fetch(`${API_BASE_URL}/api/corel`)
            ]);

            const ratingData = await ratingRes.json();
            const corelData = await corelRes.json();

            renderRatingChart(ratingData);
            renderCorrelationChart(corelData);
            renderMap(corelData); // For now, passing corelData, will need map geojson logic
            renderDataTable(corelData);

        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    }

    // --- Chart Rendering ---

    function renderRatingChart(data) {
        if (!data || data.length === 0) return;

        const container = document.getElementById('rating-chart');

        // Prepare data for Plotly
        const x = data.map(d => d.avg_review_score);
        const y = data.map(d => d.delivery_status);
        const text = data.map(d => d.total_orders);
        const colors = data.map(d => d.delivery_status === 'Late Delivery' ? '#A0001B' : '#05B431');

        const trace = {
            x: x,
            y: y,
            type: 'bar',
            orientation: 'h',
            text: text,
            marker: { color: colors },
            textposition: 'auto'
        };

        const layout = {
            title: 'Average Review Score by Delivery Status',
            xaxis: { title: 'Rating' },
            yaxis: { title: 'Delivery Status' },
            margin: { l: 150, r: 20, t: 40, b: 40 }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    function renderCorrelationChart(data) {
        if (!data || data.length === 0) return;

        const container = document.getElementById('correlation-chart');

        const x = data.map(d => d.avg_weight_per_order);
        const y = data.map(d => d.Delay_Rate);
        const text = data.map(d => d.seller_city);

        const scatterTrace = {
            x: x,
            y: y,
            mode: 'markers',
            type: 'scatter',
            text: text,
            marker: {
                size: 8,
                color: x,
                colorscale: 'Pinkyl',
                showscale: true
            },
            name: 'Data Points'
        };

        // Linear Regression (Trendline)
        const trendlineTrace = calculateTrendline(x, y);

        const layout = {
            title: 'Correlation: Product Weight vs Delay Rate',
            xaxis: { title: 'Average Weight (g)', rangemode: 'tozero' },
            yaxis: { title: 'Delay Rate (%)' },
            margin: { l: 50, r: 20, t: 40, b: 40 },
            showlegend: false
        };

        Plotly.newPlot(container, [scatterTrace, trendlineTrace], layout, { responsive: true });
    }

    function calculateTrendline(x, y) {
        // Simple linear regression (y = mx + b)
        const n = x.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;

        for (let i = 0; i < n; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumXX += x[i] * x[i];
        }

        const m = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const b = (sumY - m * sumX) / n;

        // Generate points for the line
        const minX = Math.min(...x);
        const maxX = Math.max(...x);

        return {
            x: [minX, maxX],
            y: [m * minX + b, m * maxX + b],
            mode: 'lines',
            type: 'scatter',
            name: 'Trendline',
            line: { color: 'red' }
        };
    }

    // Map rendering requires GeoJSON. 
    // We'll fetch the GeoJSON file relative to the frontend.
    async function renderMap(data) {
        try {
            const container = document.getElementById('map-chart');

            // Backend should expose this file as a static asset
            const response = await fetch('/brazil_geo.json');
            const geojson = await response.json();

            // Prepare Map Data
            // We need to match seller_state with geojson features
            // Assuming data has 'seller_state' (2-letter code) and GeoJSON has 'id' handling that.

            // Filter valid states
            data.forEach(d => {
                if (d.seller_state) d.seller_state = d.seller_state.trim().toUpperCase();
            });

            const trace = {
                type: 'choroplethmapbox', // or choropleth_map if using Plotly 2.x+ specific
                geojson: geojson,
                locations: data.map(d => d.seller_state),
                z: data.map(d => d.Delay_Rate),
                featureidkey: 'id',
                colorscale: 'Reds',
                marker: { opacity: 0.5 },
                zmin: 0,
                zmax: Math.max(...data.map(d => d.Delay_Rate))
            };

            const layout = {
                title: 'Geographical map of deliveries',
                mapbox: {
                    style: "carto-positron",
                    center: { lat: -14.235, lon: -51.925 },
                    zoom: 3
                },
                margin: { l: 0, r: 0, t: 40, b: 0 }
            };

            Plotly.newPlot(container, [trace], layout, { responsive: true });

        } catch (e) {
            console.error('Map rendering failed:', e);
            document.getElementById('map-chart').innerHTML = `<p style="padding:1rem">Could not load map data: ${e.message}</p>`;
        }
    }

    function renderDataTable(data) {
        if (!data) return;
        const container = document.getElementById('data-table-container');

        let html = '<table style="width:100%; border-collapse: collapse;">';
        // Headers
        if (data.length > 0) {
            html += '<thead><tr style="background:#f0f2f6; text-align:left;">';
            Object.keys(data[0]).forEach(key => {
                html += `<th style="padding:8px; border:1px solid #ddd;">${key}</th>`;
            });
            html += '</tr></thead>';
        }

        // Body
        html += '<tbody>';
        // Limit to 50 rows for performance
        data.slice(0, 50).forEach(row => {
            html += '<tr>';
            Object.values(row).forEach(val => {
                html += `<td style="padding:8px; border:1px solid #ddd;">${val}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;
    }

    // --- Initialization ---
    checkApiStatus();
    fetchAndRenderData();

    refreshBtn.addEventListener('click', () => {
        checkApiStatus();
        // optionally refresh data too
    });
});
