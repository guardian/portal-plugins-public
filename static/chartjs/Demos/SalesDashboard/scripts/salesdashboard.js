SalesDashboard.dashboardModel = function() {
    var self = this,
        tmpDate;

    self.dailySales = [];
    self.dailySalesDateName = "";
    self.monthlySales = [];
    self.monthlySalesDateName = "";
    self.salesPerf = {};
    self.monthActive = !SalesDashboard.isPhone;

   
    self.getDailySales = function (day) {
        function setSales(data) {
            $.each(data || [], function (i, val) {
                var tmp = new Date(val.SaleDate);
                val.SaleDate = new Date(tmp.getUTCFullYear(), tmp.getUTCMonth(), tmp.getUTCDate(), tmp.getUTCHours(), tmp.getUTCMinutes(), tmp.getUTCSeconds());
            });
            firstTime = !self.dailySales.length;
            self.dailySales = data || [];
            self.dailySalesDateName = Globalize.format(day, 'MM/dd/yy');
            if (self.dailySales.length < 3 && firstTime) {
                SalesDashboard.getLastDaySales();
                return;
            }
            self.drawDailyChart();
        }
        $('#dailySalesChart').dxChart('showLoadingIndicator');
        SalesDashboard.loadData({ day: Globalize.format(day, 'yyyy-MM-dd') }, setSales);
    };

    self.getMonthlySales = function (month) {
        function setSales(data) {
            $.each(data, function (i, val) {
                var tmp = new Date(val.SaleDate);
                val.SaleDate = new Date(tmp.getUTCFullYear(), tmp.getUTCMonth(), tmp.getUTCDate(), tmp.getUTCHours(), tmp.getUTCMinutes(), tmp.getUTCSeconds());
            });
            firstTime = !self.monthlySales.length;
            self.monthlySales = data || [];
            self.monthlySalesDateName = Globalize.format(month, 'MMM yyyy');
            if (self.monthlySales.length < 3 && firstTime) {
                SalesDashboard.getLastMonthSales();
                return;
            }
            self.drawMonthlyChart();
        }
        if (self.monthActive) $('#monthlySalesChart').dxChart('showLoadingIndicator');
        SalesDashboard.loadData({ month: Globalize.format(month, 'yyyy-MM-dd') }, setSales);

    };
    self.init = function () {

        SalesDashboard.loadData({}, function (salesPerfDto) {
            SalesDashboard.pushToMarkup({
                annualPerfLastYearSales: { value: salesPerfDto.AnnualPerformance.LastYearSales, class: true },
                fiscalYear: { value: ((new Date().getFullYear()) - 1), text: true },
                annualPerfYTDSales: { value: salesPerfDto.AnnualPerformance.YTDSales },

                dTodaySales: { value: salesPerfDto.DailyPerformance.TodaySales, fixed: 2 },
                dYesterdaySales: { value: salesPerfDto.DailyPerformance.YesterdaySales, fixed: 2 },
                dLastWeekSales: { value: salesPerfDto.DailyPerformance.LastWeekSales, fixed: 2 },

                mThisMonthSales: { value: salesPerfDto.MonthlyPerformance.ThisMonthSales },
                mLastMonthSales: { value: salesPerfDto.MonthlyPerformance.LastMonthSales },
                mYTDSales: { value: salesPerfDto.MonthlyPerformance.YTDSales },
                currentYear: { value: "(" + Globalize.format(new Date(), "yyyy") + ")", text: true }
            });

            self.salesPerf = salesPerfDto;
            if (!SalesDashboard.isPhone) {
                self.drawPerfGaugeYTDSales();
                self.drawPerfGaugeLastYearSales();
                self.drawForecastGraph();
                self.drawPieChart();
            }
        });


        self.drawDailyChart();
        SalesDashboard.getThisDaySales();

        self.drawMonthlyChart();
        SalesDashboard.getThisMonthSales();

    }

    self.drawPerfGaugeYTDSales = function () {
        var instance = $("#perfGaugeYTDSales").data("dxCircularGauge");
        if (instance) {
            instance.option("value", self.salesPerf.AnnualPerformance.YTDSales);
            instance.option("subvalues", self.salesPerf.AnnualPerformance.ForecastSales);
        } else {
            $("#perfGaugeYTDSales").dxCircularGauge({
                scale: {
                    label: { visible: false },
                    startValue: 0,
                    endValue: 450000000,
                    majorTick: {
                        tickInterval: 150000000,
                        width: 6
                    }
                },
                valueIndicator: {
                    type: 'rectangle',
                    color: '#aaaaaa',
                    width: 3,
                    spindleSize: 21,
                    spindleGapSize: 15,
                    offset: 5
                },
                value: self.salesPerf.AnnualPerformance.YTDSales,
                subvalues: self.salesPerf.AnnualPerformance.ForecastSales,
                subvalueIndicator: {
                    type: 'triangle',
                    color: '#089e60'
                },
                rangeContainer: {
                    width: 3,
                    ranges: [
                        {
                            startValue: 0,
                            endValue: 150000000,
                            color: '#db2e3e'
                        },
                        {
                            startValue: 150000000,
                            endValue: 300000000,
                            color: '#f55f40'
                        },
                        {
                            startValue: 300000000,
                            endValue: 450000000,
                            color: '#089e60'
                        }
                    ]
                }
            });
        }
    }

    self.drawPerfGaugeLastYearSales = function () {
        var instance = $("#perfGaugeLastYearSales").data("dxCircularGauge");
        if (instance) {
            instance.option("value", self.salesPerf.AnnualPerformance.LastYearSales);
        } else {
            $("#perfGaugeLastYearSales").dxCircularGauge({
                scale: {
                    label: { visible: false },
                    startValue: 0,
                    endValue: 450000000,
                    majorTick: {
                        tickInterval: 150000000,
                        width: 6
                    }
                },
                valueIndicator: {
                    type: 'rectangle',
                    color: '#aaaaaa',
                    width: 3,
                    spindleSize: 21,
                    spindleGapSize: 15,
                    offset: 5
                },
                value: self.salesPerf.AnnualPerformance.LastYearSales,
                subvalues: [],
                rangeContainer: {
                    width: 3,
                    ranges: [
                        {
                            startValue: 0,
                            endValue: 150000000,
                            color: '#db2e3e'
                        },
                        {
                            startValue: 150000000,
                            endValue: 300000000,
                            color: '#f55f40'
                        },
                        {
                            startValue: 300000000,
                            endValue: 450000000,
                            color: '#089e60'
                        }
                    ]
                }
            });
        }
    }

    self.drawForecastGraph = function() {
        var instance = $("#forecastGraph").data("dxLinearGauge");
        if (instance) {
            instance.option("value", ((self.salesPerf.AnnualPerformance.YTDSales / self.salesPerf.AnnualPerformance.ForecastSales) * 100));
        } else {
            $("#forecastGraph").dxLinearGauge({
                scale: {
                    startValue: 0,
                    endValue: 100,
                    hideFirstTick: true,
                    hideLastTick: true,
                    majorTick: {
                        showCalculatedTicks: false,
                        customTickValues: [0, 20, 70, 100]
                    },
                    label: {
                        indentFromTick: 10,
                        font: {
                            color: '#373737',
                            opacity: 0.75,
                            size: 12
                        }
                    }
                },
                valueIndicator: {
                    color: '#b0324f',
                    backgroundColor: '#e8e8e9',
                    offset: -13
                },
                value: ((self.salesPerf.AnnualPerformance.YTDSales / self.salesPerf.AnnualPerformance.ForecastSales) * 100),
                rangeContainer: {
                    backgroundColor: 'none',
                    ranges: [
                        {
                            startValue: 0,
                            endValue: 20,
                            color: '#db2e3e'
                        },
                        {
                            startValue: 20,
                            endValue: 70,
                            color: '#f55f40'
                        },
                        {
                            startValue: 70,
                            endValue: 100,
                            color: '#089e60'
                        }
                    ]
                }
            });
        }
    }

    self.drawPieChart = function() {
        var instance = $("#pieChart").data("dxPieChart");
        if (instance) {
            instance.option("dataSource", self.salesPerf.SalesBySector);
        } else {
            $("#pieChart").dxPieChart({
                palette: SalesDashboard.getCurrentPaletteName(),
                dataSource: self.salesPerf.SalesBySector,
                series: { type: 'doughnut', innerRadius: 0.55, argumentField: 'Criteria', valueField: 'Sales' },
                legend: {
                    columnItemSpacing: 7,
                    verticalAlignment: 'bottom',
                    horizontalAlignment: 'center',
                    rowCount: 2,
                    itemTextPosition: 'right',
                    customizeText: function () {
                        return this.seriesName.toUpperCase();
                    },
                    font: {
                        color: '#373737',
                        size: 12,
                        opacity: 1
                    }
                }
            });
        }
    }

    self.drawDailyChart = function () {
        var instance = $("#dailySalesChart").data("dxChart");
        if (instance) {
            instance.option("series.name", self.dailySalesDateName);
            instance.option("dataSource", self.dailySales);
        } else {
            $("#dailySalesChart").dxChart({
                theme: SalesDashboard.isPhone ? "SalesDashboardMobileTheme" : "SalesDashboardTabletTheme",
                palette: SalesDashboard.getCurrentPaletteName(),
                dataSource: self.dailySales,
                series: {
                    color: SalesDashboard.getColor("series.color", 0),
                    argumentField: 'SaleDate',
                    valueField: 'Sales',
                    name: self.dailySalesDateName,
                    point: {
                        color: SalesDashboard.getColor("series.point.color", 0),
                        border: {
                            color: SalesDashboard.getColor("", 0)
                        },
                        hoverStyle: {
                            border: {
                                color: SalesDashboard.getColor("", 0)
                            }
                        }
                    }
                },
                
                valueAxis: {
                    min: 0,
                    label: {
                        customizeText: function () { return this.value / 1000; }
                    }
                },
                argumentAxis: {
                    valueMarginsEnabled: false,
                    placeholderSize: 25,
                    argumentType: 'datetime',
                    tickInterval: { hours: 1 },
                    label: {
                        overlappingBehavior: { mode: 'ignore' },
                        format: 'h:mmtt',
                        customizeText: function () {
                            if (this.value.getHours() % 2 &&
                                this.value.getHours() !== (new Date(self.dailySales[self.dailySales.length - 1].SaleDate).getHours())) {
                                return this.valueText;
                            }
                            return '';
                        }
                    }
                },
                tooltip: {
                    paddingLeftRight: 10,
                    paddingTopBottom: 4,
                    enabled: true,
                    precision: 2,
                    format: 'millions',
                    customizeText: function () {
                        return '$' + this.valueText;
                    }
                },
                legend: {
                    markerSize: 10,
                    margin: 5,
                    paddingLeftRight: 5,
                    paddingTopBottom: 5,
                    verticalAlignment: 'top',
                    horizontalAlignment: 'left',
                    position: 'inside',
                    border: {
                        visible: true,
                        color: '#d2d2d2',
                        opacity: 1
                    },
                    font: {
                        color: '#373737',
                        opacity: 1,
                        size: 12
                    }
                }
                

            });
        }
    }

    self.drawMonthlyChart = function () {
        var instance = $("#monthlySalesChart").data("dxChart");
        if (instance) {
            instance.option("series.name", self.monthlySalesDateName);
            instance.option("dataSource", self.monthlySales); 
        } else {
            $("#monthlySalesChart").dxChart({
                theme: SalesDashboard.isPhone ? "SalesDashboardMobileTheme" : "SalesDashboardTabletTheme",
                palette: SalesDashboard.getCurrentPaletteName(),
                dataSource: self.monthlySales,
                series: {
                    argumentField: 'SaleDate',
                    valueField: 'Sales',
                    color: SalesDashboard.getColor("series.color", 2),
                    name: self.monthlySalesDateName,
                    point: {
                        color: SalesDashboard.getColor("series.point.color", 2),
                        border: {
                            color: SalesDashboard.getColor("", 2)
                        },
                        hoverStyle: {
                            border: {
                                color: SalesDashboard.getColor("", 2)
                            }
                        }
                    }
                },
                valueAxis: {
                    min: 500000,
                    tickInterval: 500000,
                    label: {
                        precision: 1,
                        format: 'millions'
                    }
                },
                argumentAxis: {
                    valueMarginsEnabled: false,
                    argumentType: 'datetime',
                    placeholderSize: 25,
                    tickInterval: {
                        days: 3
                    },
                    label: {
                        overlappingBehavior: { mode: 'ignore' },
                        format: 'M/dd',
                        customizeText: function () {
                            if (this.value.getDate() === 1 ||
                                this.value.getDate() === (new Date(self.monthlySales[self.monthlySales.length - 1].SaleDate).getDate())) {
                                return '';
                            }
                            return this.valueText;
                        }
                    }
                },
                tooltip: {
                    paddingLeftRight: 10,
                    paddingTopBottom: 4,
                    enabled: true,
                    precision: 2,
                    format: 'millions',
                    customizeText: function () {
                        return '$' + this.valueText;
                    }
                },
                legend: {
                    markerSize: 10,
                    margin: 5,
                    paddingLeftRight: 5,
                    paddingTopBottom: 5,
                    verticalAlignment: 'top',
                    horizontalAlignment: 'left',
                    position: 'inside',
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
                
            });
        }
    }

    self.redrawGraph = function (id) {
        if (id == "#day") {
            self.monthActive = false;
            self.drawDailyChart();
        } else {
            self.monthActive = true;
            self.drawMonthlyChart();
        }
    }
   
}

SalesDashboard.currentModel = new SalesDashboard.dashboardModel();
SalesDashboard.currentModel.init();

