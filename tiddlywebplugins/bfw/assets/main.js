/*jslint white: true, vars: true, browser: true */
/*global Checklists, jQuery */

(function($) {

"use strict";

new Checklists("article", retriever, storer);

function retriever(checkbox, callback) {
	$.ajax({
		type: "get",
		url: document.location.toString(),
		dataType: "text",
		success: callback
		// TODO: error handling
	});
}

function storer(markdown, checkbox, callback) {
	$.ajax({
		type: "put",
		url: document.location.toString(),
		data: markdown,
		contentType: "application/json",
		success: callback
		// TODO: error handling
	});
}

}(jQuery));
