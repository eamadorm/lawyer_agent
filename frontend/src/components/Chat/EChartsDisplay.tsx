import React from 'react';
import ReactECharts from 'echarts-for-react';

interface EChartsDisplayProps {
    echartsData: any[]; // Data from the API response
}

const COLORS = [
    '#2962FF', // Blue A700
    '#FF6D00', // Orange A700
    '#00C853', // Green A700
    '#D50000', // Red A700
    '#AA00FF', // Purple A700
    '#00B8D4', // Cyan A700
    '#C51162', // Pink A700
    '#FFAB00', // Amber A700
    '#304FFE', // Indigo A700
    '#AEEA00', // Lime A700
    '#0091EA', // Light Blue A700
    '#6200EA', // Deep Purple A700
    '#DD2C00', // Deep Orange A700
    '#00BFA5'  // Teal A700
];

export const EChartsDisplay: React.FC<EChartsDisplayProps> = ({ echartsData }) => {
    if (!echartsData || echartsData.length === 0) {
        return null;
    }

    const getOption = (chartData: any) => {
        // Detect chart type based on data structure
        // Stacked Bar has 'xaxis_categories' and 'series_list'
        if (chartData.xaxis_categories && chartData.series_list) {
            return {
                title: {
                    text: chartData.title,
                    left: 'center',
                    textStyle: { fontFamily: 'Inter, sans-serif' }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' }
                },
                legend: {
                    bottom: 0,
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '10%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: chartData.xaxis_categories
                },
                yAxis: chartData.chart_type === 'mixed' ? [
                    {
                        type: 'value',
                        name: 'Primary',
                        position: 'left',
                        axisLine: { show: true },
                        axisLabel: { formatter: '{value}' }
                    },
                    {
                        type: 'value',
                        name: 'Secondary',
                        position: 'right',
                        axisLine: { show: true },
                        axisLabel: { formatter: '{value}' },
                        splitLine: { show: false } // Avoid grid mess
                    }
                ] : {
                    type: 'value'
                },
                series: chartData.series_list.map((series: any, index: number) => {
                    const isArea = chartData.chart_type === 'area';
                    const isMixed = chartData.chart_type === 'mixed';

                    let seriesType = isArea ? 'line' : 'bar';
                    if (isMixed && series.type) {
                        seriesType = series.type;
                    }

                    return {
                        name: series.name,
                        type: seriesType,
                        yAxisIndex: isMixed ? (series.y_axis_index || 0) : 0,
                        stack: isMixed ? undefined : 'total', // Mixed charts usually don't stack bars and lines together
                        areaStyle: isArea ? {} : undefined,
                        data: series.data,
                        itemStyle: {
                            color: COLORS[index % COLORS.length]
                        }
                    };
                })
            };
        }

        // Pie Chart has 'data_points'
        if (chartData.data_points) {
            return {
                title: {
                    text: chartData.title,
                    left: 'center',
                    textStyle: { fontFamily: 'Inter, sans-serif' }
                },
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    orient: 'vertical',
                    left: 'left'
                },
                series: [
                    {
                        name: 'Access From',
                        type: 'pie',
                        radius: ['40%', '70%'],
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        label: {
                            show: false,
                            position: 'center'
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: 40,
                                fontWeight: 'bold'
                            }
                        },
                        labelLine: {
                            show: false
                        },
                        data: chartData.data_points.map((point: any, index: number) => ({
                            ...point,
                            itemStyle: {
                                color: COLORS[index % COLORS.length]
                            }
                        }))
                    }
                ]
            };
        }

        return {};
    };

    return (
        <div className="echarts-display-container" style={{ width: '100%', height: '100%' }}>
            {echartsData.map((chart, idx) => (
                <div key={idx} className="chart-card" style={{ height: '400px', marginBottom: '20px' }}>
                    <ReactECharts
                        option={getOption(chart)}
                        style={{ height: '100%', width: '100%' }}
                        opts={{ renderer: 'svg' }}
                        notMerge={true}
                    />
                </div>
            ))}
        </div>
    );
};
