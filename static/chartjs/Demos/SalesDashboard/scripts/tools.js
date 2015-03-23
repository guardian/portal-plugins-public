function SalesDashboard() {
    var self = this,
        tmpDate = new Date(),
        nextYearId = "#nextYear",
        daySwitcher = "Day",
        monthSwitcher = "Month",
        colorDict = {
            "series.point.color": { phone: "#cf5777", tablet: undefined },
            "series.color": { phone: "#fff", tablet: undefined },
        },

        switcherData = {
            "#getPrevDaySales": { click: function () { self.getPrevDaySales() } },
            "#getNextDaySales": { click: function () { self.getNextDaySales() }, role: "next" },
            "#getLastDaySales": { click: function () { self.getLastDaySales() }, role: "last" },
            "#getThisDaySales": { click: function () { self.getThisDaySales() }, role: "today" },
             
            "#getPrevMonthSales": { click: function () { self.getPrevMonthSales() } },
            "#getNextMonthSales": { click: function () { self.getNextMonthSales() }, role: "next"  },
            "#getLastMonthSales": { click: function () { self.getLastMonthSales() }, role: "last"  },
            "#getThisMonthSales": { click: function () { self.getThisMonthSales() }, role: "today" },

            "#prevYear": { click: function () { self.changeRangeYear(-1); } },
            "#nextYear": { click: function () { self.changeRangeYear(1); } }
        }

    self.tabletPalette = "salesDashboardPaletteTablet";
    self.mobilePalette = "salesDashboardPaletteMobile";

    self.baseApiUrl = "http://demos.devexpress.com/DevExtreme/SalesDashboard/api/";
    self.apiCategory = "";
    self.isPhone = undefined;
    self.showingCategory = "";
    self._currentDay = new Date(tmpDate.getFullYear(), tmpDate.getMonth(), tmpDate.getDate(), 0, 0, 0);
    self._currentMonth = new Date(tmpDate.getFullYear(), tmpDate.getMonth(), 1, 0, 0, 0);
    self.rangeYear = new Date().getFullYear();
    self.currentModel = null;
    self.pushToMarkup = function (values) {
        var convertVal = function (value, fixed, prefix, postfix, divider) {
            return prefix + ((value || 0) / divider).toFixed(fixed) + postfix;
        }

        $.each(values, function (id, item) {
            $((item.class ? "." : "#") + id)
                .text(item.text
                    ? item.value
                    : convertVal(
                        item.value,
                        item.fixed,
                        item.prefix !== undefined ? item.prefix : '$',
                        item.postfix !== undefined ? item.postfix : 'M',
                        item.divider !== undefined ? item.divider : 1000000)
                    );
        });
    };
    self.loadPage = function (activeTab) {
        var url = "";
        self.apiCategory = activeTab ? activeTab.toLowerCase() : "index";
        switch (self.apiCategory) {
            case "index":
                url = "SalesDashboard";
                break;
            case "products":
                url = "CriteriaSales";
                break;
            case "sectors":
                url = "CriteriaSales";
                break;
            case "regions":
                url = "CriteriaSales";
                break;
            case "channels":
                url = "Channels";
                break;
            case "map":
                url = "Map";
                break;
            default:
                url = "SalesDashboard";
        }
        self.showingCategory = activeTab.charAt(0).toUpperCase() + activeTab.slice(1, -1);
        
        self.rangeYear = new Date().getFullYear();
        $('.navigation-item').removeClass('active');
        $('#' + self.apiCategory + '.navigation-item').addClass('active');
        $("#dashboard-content").load(["views/", url, ".html"].join(""), function () {
            self.initializeSwitchers();
        });
        return false;
    };
    self.loadData = function (data, callback, isCategory, category) {
        $.ajax({
            url: self.baseApiUrl + (isCategory ? (category || self.apiCategory) : "sales"),
            dataType: "jsonp",
            data: data,
            success: callback
        });
    };

    self.initializeSwitchers = function(){
        $.each(switcherData, function (id, value) {
            $(id).click(value.click);
        });

        $(".phone-switcher div").click(self.changeGraphType);
    };
    
    self.getLastDaySales = function () {
        var tmp = new Date();
        self._currentDay = new Date(tmp.getFullYear(), tmp.getMonth(), tmp.getDate() - 1, 0, 0, 0);
        self.updateSwitcher(daySwitcher);
    };

    self.getPrevDaySales = function () {
        var curDate = self._currentDay;
        self._currentDay = new Date(curDate.setDate(curDate.getDate() - 1));
        self.updateSwitcher(daySwitcher);
    };

    self.getNextDaySales = function () {
        var tmp = new Date(),
            curDate = self._currentDay;
        if (curDate.getFullYear() === tmp.getFullYear()
            && curDate.getMonth() === tmp.getMonth()
            && curDate.getDate() === tmp.getDate()) {
            return;
        }
        self._currentDay = new Date(curDate.setDate(curDate.getDate() + 1));
        self.updateSwitcher(daySwitcher);
    },

    self.getThisDaySales = function () {
        var tmp = new Date();
        self._currentDay = new Date(tmp.getFullYear(), tmp.getMonth(), tmp.getDate(), 0, 0, 0);
        self.updateSwitcher(daySwitcher);
    };

    self.getThisMonthSales = function () {
        var tmp = new Date();
        self._currentMonth = new Date(tmp.getFullYear(), tmp.getMonth(), 1, 0, 0, 0);
        self.updateSwitcher(monthSwitcher);
    };

    self.getLastMonthSales = function () {
        var tmp = new Date();
        self._currentMonth = new Date(tmp.getFullYear(), tmp.getMonth() - 1, 1, 0, 0, 0);
        self.updateSwitcher(monthSwitcher);
    };

    self.getPrevMonthSales = function () {
        var curDate = self._currentMonth;
        self._currentMonth = new Date(curDate.setMonth(curDate.getMonth() - 1));
        self.updateSwitcher(monthSwitcher);
    };

    self.getNextMonthSales = function () {
        var tmp = new Date(),
            curDate = self._currentMonth;
        if (curDate.getFullYear() === tmp.getFullYear()
            && curDate.getMonth() === tmp.getMonth()) {
            return;
        }
        self._currentMonth = new Date(curDate.setMonth(curDate.getMonth() + 1));
        self.updateSwitcher(monthSwitcher);
    };

    self.updateSwitcher = function (switcher) {
        var tmp = new Date(),
            isDay = (switcher == daySwitcher),
            current = isDay ? self._currentDay : self._currentMonth,
            todayDate = new Date(tmp.getFullYear(), tmp.getMonth(), isDay ? tmp.getDate() : 1),
            lastDate = new Date(tmp.getFullYear(), isDay ? tmp.getMonth() : tmp.getMonth() - 1, isDay ? tmp.getDate() - 1 : 1),
            valueDate = new Date(current.getFullYear(), current.getMonth(), isDay ? current.getDate() : 1);

        if(self.currentModel)
            isDay ? self.currentModel.getDailySales(current) : self.currentModel.getMonthlySales(current);

        $.each(switcherData, function (id, value) {
            if (id.indexOf(switcher) != -1) {
                $(id).removeClass("active").removeClass("disabled");
                if (valueDate.getTime() == todayDate.getTime()) {
                    if (value.role === "today") $(id).addClass("active");
                    if (value.role === "next") $(id).addClass("disabled");
                } else if (valueDate.getTime() == lastDate.getTime()) {
                    if (value.role === "last") $(id).addClass("active");
                }
            }
        });
    }
    
    self.changeRangeYear = function (offset) {
        var newYear = self.rangeYear + offset,
            newStart = new Date(newYear, 0, 1),
            newEnd = new Date(newYear, 11, 31);

        if (newYear > new Date().getFullYear()) {
            return;
        }

        function setRangeYear(year) {
            self.rangeYear = year;
            $("#rangeYearName").text("(" + self.rangeYear + ")");
            $(nextYearId).removeClass("disabled");
            if (year >= new Date().getFullYear()) {
                $(nextYearId).addClass("disabled");
            }
        }

        self.loadData({
            startDate: Globalize.format(newStart, 'yyyy-MM-dd'),
            endDate: Globalize.format(newEnd, 'yyyy-MM-dd')
        }, function (data) {
            if (data && data.length)
                setRangeYear(newYear);
        }, true);

        self.loadData({
            startDate: Globalize.format(newStart, 'yyyy-MM-dd'),
            endDate: Globalize.format(newEnd, 'yyyy-MM-dd')
        },
            function (data) {
                if (data && data.length) {
                    self.currentModel.salesRangeSelectedRange = {
                        startValue: new Date(data[0].SaleDate),
                        endValue: new Date(data[data.length - 1].SaleDate)
                    };
                    self.currentModel.salesRange = data;
                    setRangeYear(newYear);
                    self.currentModel.drawRangeSelector(true);
                }
            });
    }

    self.changeGraphType = function (element) {
        if ($(this).hasClass("selected")) return;
        $(this).siblings().removeClass("selected");
        $(this).addClass("selected");
        $($(this).siblings().attr("data-show")).addClass("phone-hide");
        $($(this).attr("data-show")).removeClass("phone-hide");
        self.currentModel.redrawGraph($(this).attr("data-show"));
    }

    self.getColor = function (objectName, paletteIndex) {
        var color = null;
        if (colorDict[objectName])
            color = self.isPhone ? colorDict[objectName].phone : colorDict[objectName].tablet;
        return color ? color : self._getPalette()[parseInt(paletteIndex) || 0];
    }
    
    self.getCurrentPaletteName = function(){
            return self.isPhone ? self.mobilePalette : self.tabletPalette;
    }

    self._getPalette = function () {
        return self.isPhone ?
            DevExpress.viz.core.getPalette(self.mobilePalette) :
            DevExpress.viz.core.getPalette(self.tabletPalette);
        
    }

    self.setScreenSize = function () {
        var old = self.isPhone,
            el = $("<div>").addClass("screen-size").appendTo("body"),
            size = getComputedStyle(el[0], ":after").content.replace(/"/g, "");
        el.remove();
        self.isPhone = (size === "small");
        if (typeof old != "undefined" && old != self.isPhone) self.loadPage(self.apiCategory);
    };

}

$(function () {
    window.SalesDashboard = new SalesDashboard();
    
    $("a").each(function () {
        if (!this.onclick && this.getAttribute("target") != "_blank") {
            this.onclick = function () {
                return SalesDashboard.loadPage(this.getAttribute("href"));
            };
        }
    });
    $(window).bind("resize", SalesDashboard.setScreenSize);
    SalesDashboard.setScreenSize();
    $("#currentDate").text((Globalize.format(new Date(), "MMM d, yyyy")).toUpperCase());
    SalesDashboard.loadPage("Index");
});
