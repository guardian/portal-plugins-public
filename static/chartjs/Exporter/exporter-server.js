    "use strict";
///#DEBUG
var _this = {};
///#ENDDEBUG

   var config = {
       JQUERY: "jquery-2.0.3.min.js",
       TEMP_FOLDER_NAME: "Temp/",
       PDF_SCALE_KOEF: 1.57
   },
	system = require("system"),
	fileSystem = require("fs"),
	contentTypes = {
	    pdf: "application/pdf",
	    svg: "image/svg+xml",
        png: "image/png"
	};

   var getConsoleParameters = function () {
       if (system.args.length < 2) {
           console.log("Parameters are not defined!");
       }
       return {
           host: system.args[1],
           port: system.args[2]
       };
   };

   var getFileName = function(format) {
       var value = "";

       for (var i = 0; i < 32; i++) {
           value += Math.round(Math.random() * 16).toString(16);
       }

       return config.TEMP_FOLDER_NAME + value + "." + format;
   };

   var createAndWriteFile = function (fileTEMP_FOLDER_NAME, contentWrite) {
       var svgFile = fileSystem.open(fileTEMP_FOLDER_NAME, "w");
       svgFile.flush();
       svgFile.write(contentWrite);
       svgFile.close();
   };

   var prepareHtmlContent = function (page, exportContent, svgElements) {
       var svgFilesPath = [];

       page.injectJs(config.JQUERY);

       svgElements = JSON.parse(svgElements);

       for (var i = 0; i < svgElements.length; i++) {
           svgFilesPath.push(getFileName("svg"));
           createAndWriteFile(svgFilesPath[i], svgElements[i]);
       }
       page.evaluate(function (svgFilesPath, svgElements) {
           var $object;


           $(document.body).css("background-color", "#ffffff").append(svgElements);

           $(document.body).find("svg").each(function (key) {
               $object = $("<object>")
			.css({
			    width: $(this).width(),
			    height: $(this).height()
			})
			.attr({
			    data: "../" + svgFilesPath[key],
			    type: "image/svg+xml"
			});
               $(this).wrap("<div>").parent().html("").append($object);
               $object.unwrap();
           });

       }, svgFilesPath, svgElements);
       return svgFilesPath;
   };

   var render = function (options, renderCompleted) {
       var page = require("webpage").create();

       page.open(options.htmlFileName, function (status) {
           if (status !== "success") {
               options.response.close();
           } else {
               switch (options.format) {
                   case "pdf":
                       options.width *= config.PDF_SCALE_KOEF;
                       options.height *= config.PDF_SCALE_KOEF;
                       page.viewportSize = page.paperSize = {
                           width: options.width,
                           height: options.height
                       };
                       break;
                   case "svg":
                       options.exportFileName = options.filesPath[0];
                       break;
               }
               
               page.render(options.exportFileName);

               fileSystem.remove(options.htmlFileName);

               page.close();

               renderCompleted(options);
           }
       });
   };

   var renderCompleted = function (parameters) {
       var exportFile =  fileSystem.open( parameters.exportFileName , "rb"),
           exportFileContent = exportFile.read();

       parameters.response.statusCode = 200;
       parameters.response.headers = {
           "Access-Control-Allow-Origin": parameters.url,
           "Content-Type": contentTypes[parameters.format],
           "Content-Disposition": "attachment; fileName=" + parameters.fileName + "." + parameters.format,
           "Content-Length": exportFileContent.length
       };
       parameters.response.setEncoding("binary");
       parameters.response.write(exportFileContent);
     
       exportFile.close();

       parameters.format !== "svg" && fileSystem.remove(parameters.exportFileName);

       for (var i = 0; i < parameters.filesPath.length; i++) {
           fileSystem.remove(parameters.filesPath[i]);
       }

       parameters.filesPath = [];

       parameters.response.close();
   };

   function getOptions(request) {
       var self = this;
        ///#DEBUG
       self = self ? self : _this;
        ///#ENDDEBUG
       if (request.post) {
           self.exportContent = request.post.exportContent;
           self.svgElements = request.post.svgElements;
           self.format = request.post.format;
           self.fileName = request.post.fileName;
           self.width = request.post.width;
           self.height = request.post.height;
           self.url = request.post.url;
       }
       return {
           exportContent: self.exportContent,
           svgElements: self.svgElements,
           format: self.format,
           fileName: self.fileName,
           width: self.width,
           height: self.height,
           url : self.url 
       }
   };

   var requestHandler = function (request, response) {
       var svgFilesPath,
           htmlFileName = getFileName("html"),
           page,
           options = getOptions(request),
           msg;
       try {
           page = require("webpage").create();
           svgFilesPath = prepareHtmlContent(page, options.exportContent, options.svgElements);
           createAndWriteFile(htmlFileName, page.content);
           page.close();

           render({
               htmlFileName: htmlFileName,
               exportFileName: getFileName(options.format),
               filesPath: svgFilesPath,
               fileName: options.fileName,
               format: options.format,
               width: options.width,
               height: options.height,
               url: options.url,
               response: response
           }, renderCompleted);

       } catch (e) {
           response.statusCode = 500;
           console.log("Failed rendering: \n" + e);
           response.close();
       }
   };

   var startServer = function () {
       var server = require("webserver").create(),
           args = getConsoleParameters();

       server.listen(args.host + ":" + args.port, requestHandler);
       console.log("OK, PhantomJS is ready.");
   };

  startServer();