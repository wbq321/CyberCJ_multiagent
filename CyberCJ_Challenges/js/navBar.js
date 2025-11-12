var currentIndex = 0; // start at introduction page

var navMap = {
    // Maps each content page to a key for easier page calls
    0: "Scenario1/intro1.html",  1: "Scenario1/eg1.html", 2: "Scenario1/Scen1_ref.html",
    3: "Scenario2/intro2.html", 4: "Scenario2/eg2.html", 5: "Scenario2/Scen2_notes.html",
    6: "Scenario3/intro3.html",   7: "Scenario3/eg3.html",  8: "contact.html"
};


function navigateTo(targetUrlKey) {
    var moduleSrc = $('#module').attr('src');

    // Check if the target URL key exists in the navigation map
    if (navMap.hasOwnProperty(targetUrlKey)) {
        if (moduleSrc !== navMap[targetUrlKey]) {
            // Update the src attribute with the URL from navMap
            $('#module').attr('src', navMap[targetUrlKey]);
            currentIndex = targetUrlKey;
        }
    } else {
        // Fallback: use targetUrlKey as the src and increment currentIndex
        if (moduleSrc !== targetUrlKey) {
            $('#module').attr('src', targetUrlKey);
            currentIndex = currentIndex + 1; // Incrementing the current index
        }
    }
}


$(document).ready(function() {
    // Controls dropdown sitemap menu in header
    $('#navbarDropdownSubMenuLink').click(function(e) {
        e.stopPropagation(); // Prevent the dropdown from closing on click
    });
    
    // Tracks the total number of modules in the navMap object (dictionary)
    var totalModules = Object.keys(navMap).length -1;

    // Navigation buttons change content within the #module iframe
    $('#next').click(function() {
        if ($('#module').attr('src') !== navMap[currentIndex]){
            $('#module').attr('src', navMap[currentIndex]);
        }
        else if (currentIndex < totalModules) {
            currentIndex ++;
            $('#module').attr('src', navMap[currentIndex]); // load next module
        } else {
            $('#module').attr('src', navMap[0]); // load first module
            currentIndex = 0;
        }
    });

    $('#back').click(function() {
        if (currentIndex > 0) {
            currentIndex --;
            $('#module').attr('src', navMap[currentIndex]); // load previous module
        } else {
            $('#module').attr('src', navMap[totalModules]); // load last module
            currentIndex = totalModules;
        }
    });

    $('.navBar-target').click(function(e) {
        e.preventDefault(); // Prevent default anchor click behavior
        var targetUrlKey = $(this).attr('href'); // Get navMAp key for the link
        var parentJQuery = parent.$;

        // Call the navigateTo function defined in the parent document
        parentJQuery(parent).get(0).navigateTo(targetUrlKey);
    });

    // creates a popup window for pdfs
    $('.popupLink').on('click', function(e){
        e.preventDefault(); // Prevent the default action of the link
        var url = $(this).attr('href'); // Get the href attribute of the link
        window.open(url, 'Popup', 'width=600,height=600,scrollbars=yes,resizable=yes'); // Open the link in a popup
    });

    // Handle mouse enter and leave for hover effects
    $(".iframe-container").hover(
        function() {
          // Mouse enter
          $("#IframePreview").show();
          $("#staticPreview").hide();
        },
        function() {
          // Mouse leave
          $("#IframePreview").hide();
          $("#staticPreview").show();
        }
      );
   

      // Handle click event to navigate to the external page
  $(".iframe-container").click(function() {
    window.open('https://livethreatmap.radware.com/', '_blank'); // Opens in a new tab
  });
  
});

