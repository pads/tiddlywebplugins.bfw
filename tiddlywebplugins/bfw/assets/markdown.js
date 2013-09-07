(function($) {

"use strict";

var checkboxSelector = "> li > input:checkbox";
var checklists = $("ul:has(" + checkboxSelector + ")"); // XXX: imprecise, inefficient
checklists.on("change", checkboxSelector, onChange).each(function(i, list) {
	$(checkboxSelector, list).prop("disabled", false);
});

function onChange(ev) {
	var checkbox = $(this);
	var container = checkbox.closest("[data-source]"); // XXX: inefficient
	var index = $("ul" + checkboxSelector, container).index(this);
	var uri = container.data("source");
	checkbox.prop("disabled", true);
	$.ajax({
		type: "get",
		url: uri,
		dataType: "json",
		success: function(data, status, xhr) {
			data = toggleCheckbox(index, data.text);
			store(data, uri, function(data, status, xhr) {
				checkbox.prop("disabled", false);
			});
		}
	});
}

function store(markdown, uri, callback) {
	var data = { type: "text/x-markdown", text: markdown };
	$.ajax({
		type: "put",
		url: uri,
		data: JSON.stringify(data),
		contentType: "application/json",
		success: callback
		// TODO: error handling
	});
}

function toggleCheckbox(index, markdown) {
	var pattern = /^([*-]) \[([ Xx])\]/mg; // XXX: duplicates server-side logic!?
	var count = 0;
	return markdown.replace(pattern, function(match, prefix, marker) {
		if(count === index) {
			marker = marker === " " ? "x" : " ";
		}
		count++;
		return prefix + " [" + marker + "]";
	});
}

}(jQuery));
