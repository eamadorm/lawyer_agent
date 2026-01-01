import React from 'react';
import Plot from 'react-plotly.js';

interface ChartData {
    data: any[];
    layout: any;
}

interface ChartsDisplayProps {
    charts: ChartData[];
}

export const ChartsDisplay: React.FC<ChartsDisplayProps> = ({ charts }) => {
    if (!charts || charts.length === 0) {
        return (
            <div className="charts-placeholder">
                <div className="placeholder-content">
                    <h3>Data Visualization</h3>
                    <p>Ask the agent to analyze data to see charts here.</p>
                </div>
            </div>
        );
    }

    const getGridClass = (count: number) => {
        if (count === 1) return 'grid-1';
        if (count === 2) return 'grid-2';
        if (count <= 4) return 'grid-4';
        return 'grid-6';
    };

    return (
        <div className={`charts-display-container ${getGridClass(charts.length)}`}>
            {charts.map((chart, idx) => (
                <div key={idx} className="chart-card">
                    <Plot
                        data={chart.data}
                        layout={{
                            ...chart.layout,
                            autosize: true,
                            margin: { t: 40, r: 20, l: 40, b: 40 },
                            paper_bgcolor: 'transparent',
                            plot_bgcolor: 'transparent',
                            font: { family: 'Inter, sans-serif' }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ responsive: true, displayModeBar: false }}
                    />
                </div>
            ))}
        </div>
    );
};
