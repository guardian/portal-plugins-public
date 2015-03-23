
$(function () {
    SalesDashboard.themes = [
        {
            name: "SalesDashboardMobileTheme",
            chart: {
                commonAxisSettings: {
                    placeholderSize: 30,
                    grid: {
                        visible: true,
                        color: '#d46885'
                    },
                    label: {
                        indentFromAxis: 5,
                        font: {
                            color: '#fff',
                            opacity: 0.75,
                            size: 10
                        }
                    }

                },
                commonPaneSettings: {
                    border: {
                        visible: true,
                        color: '#db8199'
                    }
                },
                commonSeriesSettings: {
                    type: 'area',
                    point:  {
                        border: { color: "#fff", visible: true, width: 2 },
                        size: 2,
                        hoverStyle: {
                            border: { color: "#fff", visible: true, width: 2 },
                            color: "#cf5777",
                            size: 4
                        }
                    },
                    border: {
                        color: '#fff',
                        width: 3,
                        visible: true
                    }
                },
                tooltip: {
                    color: "#fff",
                    font: {
                        color: '#a6465f',
                        opacity: 1,
                        size: 20,
                        weight: 700
                    },
                },
                legend: {
                    visible: false
                },
                loadingIndicator: {
                    backgroundColor: "#cf5777",
                    font: {color: "#fff"}
                }
            }
        },
        {
            name: "SalesDashboardTabletTheme",
            chart: {
                commonAxisSettings: {
                    placeholderSize: 30,
                    grid: {
                        visible: true,
                        color: '#d3d3d3'
                    },
                    label: {
                        indentFromAxis: 5,
                        font: {
                            color: '#373737',
                            opacity: 0.75,
                            size: 10
                        }
                    }

                },
                commonPaneSettings: {
                    border: {
                        visible: true,
                        color: '#d3d3d3'
                    }
                },
                commonSeriesSettings: {
                    type: 'area'
                },
                tooltip: {
                    border: { color: "#b43b57" },
                    color: "#b43b57",
                    font: {
                        color: "#fff",
                        opacity: 1,
                        size: 18
                    }
                }
            }
        },
        {
            name: "CriteriaSalesMobileTheme",
            chart: {
                commonAxisSettings: {
                    label: {
                        font: {
                            color: "#fff",
                            opacity: 0.75,
                            size: 10
                        }
                    }

                },
                commonPaneSettings: {
                    border: {
                        visible: true,
                        color: "#db8199"
                    }
                },
                commonSeriesSettings: {
                    label: {
                        font: {
                            color: '#cf5777'
                        }
                    }
                },
                valueAxis: {
                    grid: {
                        visible: true,
                        color: "#d46885"
                    }
                },
                tooltip: {
                    color: "#fff",
                    font: {
                        color: "#cf5777"
                    }
                },
                loadingIndicator: {
                    backgroundColor: "#cf5777",
                    font: { color: "#fff" }
                }
            }
        },
        {
            name: "CriteriaSalesTabletTheme",
            chart: {
                commonAxisSettings: {
                    label: {
                        font: {
                            color: "#373737",
                            opacity: 0.75,
                            size: 10
                        }
                    }

                },
                commonPaneSettings: {
                    border: {
                        visible: true,
                        color: "#d3d3d3"
                    }
                },
                commonSeriesSettings: {
                    label: {
                        font: {
                            color: '#ffffff'
                       }
                    }
                },
                valueAxis: {
                    grid: {
                        visible: true,
                        color: "#d3d3d3"
                    }
                },
                tooltip: {
                    border: { color: "#b43b57" },
                    color: "#b43b57",
                    font: {
                        color: "#fff"
                    }
                }
            }
        },
        {
            name: "ChannelsMobileTheme",
            chart: {
                legend: {
                    verticalAlignment: 'bottom',
                    paddingTopBottom: 0,
                    paddingLeftRight: 0,
                    horizontalAlignment: "center",
                    itemTextPosition: "bottom",
                    orientation: "horizontal",
                    font: {
                        color: 'white',
                        size: 12,
                        opacity: 1
                    }
                },
                loadingIndicator: {
                    backgroundColor: "#cf5777",
                    font: { color: "#fff" }
                }
            }
        },
        {
            name: "ChannelsTabletTheme",
            chart: {
                legend: {
                    margin: { top: 60, left: 2 },
                    paddingTopBottom: 10,
                    paddingLeftRight: 10,
                    columnCount: 1,
                    border: {
                        visible: true,
                        color: '#d2d2d2',
                        opacity: 1
                    },
                    font: {
                        color: '#373737',
                        size: 12,
                        opacity: 1
                    }
                }
            }
        }

    ];
    
    DevExpress.viz.core.registerPalette(SalesDashboard.tabletPalette, {
        simpleSet: ["#b0324f", "#db2e3e", "#f55f40", "#fb9f8c", "#9c5ba0", "#ae7c86"],
        indicatingSet: ['#90ba58', '#eeba69', '#a37182'],
        gradientSet: [ "#fb9f8c","#b0324f"]
    });
    DevExpress.viz.core.registerPalette(SalesDashboard.mobilePalette, {
        simpleSet: ["#f6da80", "#85e3fb", "#ecaaf0", "#ffa97f", "#b3c5ff", "#ff98a2", "#ff98a2", "#bed9ad"],
        indicatingSet: ['#90ba58', '#eeba69', '#a37182'],
        gradientSet: ['#78b6d9', '#eeba69']
    });
    $.each(SalesDashboard.themes, function (_, theme) {
        DevExpress.viz.core.registerTheme(theme);
    });
});