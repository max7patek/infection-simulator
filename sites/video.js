function switchContent(content, elmnt, color) {
  // Hide all elements with class="tabcontent" by default */
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove the background color of all tablinks/buttons
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(content).style.display = "block";

  // Add the specific color to the button used to open the tab content
  elmnt.style.backgroundColor = "#ADADAD";
}

function switchSimulations(simulations, elmnt, color) {
  // Hide all elements with class="tabcontent" by default */
  var i, casecontent, caselinks;
  casecontent = document.getElementsByClassName("casecontent");
  for (i = 0; i < casecontent.length; i++) {
    casecontent[i].style.display = "none";
  }

  // Remove the background color of all tablinks/buttons
  caselinks = document.getElementsByClassName("caselink");
  for (i = 0; i < caselinks.length; i++) {
    caselinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(simulations).style.display = "block";

  // Add the specific color to the button used to open the tab content
  elmnt.style.backgroundColor = "#ADADAD";
}

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();