var currentIndex = 0; // start at introduction page

var navMap = {
    // Maps each content page to a key for easier page calls
    0: "introduction/mod1_0.html",          1: "introduction/mod1_1.html",         2: "introduction/mod1_2.html",             3: "introduction/mod1_3.html",
    4: "introduction/mod1_review.html",     5: "https://d2hie3dpn9wvbb.cloudfront.net/risk_management/risk_management.html",  6: "introduction/mod1_kc.html",        7: "introduction/mod1_cs.html",
    8: "introduction/mod1_ref.html",        9: "computer-security/mod2_0_0.html", 10: "computer-security/mod2_1_0.html",     11: "computer-security/mod2_1_1.html",
    12: "computer-security/mod2_1_2.html", 13: "computer-security/mod2_1_3.html", 14: "computer-security/mod2_1_4.html",     15: "computer-security/mod2_1_5.html",
    16: "computer-security/mod2_2_0.html", 17: "computer-security/mod2_2_1.html", 18: "computer-security/mod2_2_2.html",     19: "computer-security/mod2_2_3.html",
    20: "computer-security/mod2_2_4.html", 21: "computer-security/mod2_3_0.html", 22: "computer-security/mod2_3_1.html",     23: "computer-security/mod2_3_2.html",
    24: "computer-security/mod2_3_3.html", 25: "computer-security/mod2_3_4.html", 26: "computer-security/mod2_3_5.html",     27: "computer-security/mod2_review.html",
    28: "https://d2hie3dpn9wvbb.cloudfront.net/ransomware/RansomwareAttack.html", 29: "https://www.pbs.org/wgbh/nova/labs//lab/cyber/research#/newuser",
    30: "computer-security/mod2_kc.html",  31: "computer-security/mod2_cs.html",
    32: "computer-security/mod2_ref.html", 33: "internet-security/mod3_0.html",   34: "internet-security/mod3_1_0.html",     35: "internet-security/mod3_2_0.html",
    36: "internet-security/mod3_3_0.html", 37: "internet-security/mod3_3_1.html", 38: "internet-security/mod3_3_2.html",     39: "internet-security/mod3_4_0.html",
    40: "internet-security/mod3_4_1.html", 41: "internet-security/mod3_4_2.html", 42: "internet-security/mod3_review.html",  43: "https://phishingquiz.withgoogle.com/",
    44: "https://d2hie3dpn9wvbb.cloudfront.net/attacks/attacks.html",             45: "internet-security/mod3_kc.html",      46: "internet-security/mod3_cs.html",      47: "internet-security/mod3_ref.html",
    48: "privacy/mod4_0.html",             49: "privacy/mod4_1.html",             50: "privacy/mod4_2_0.html",               51: "privacy/mod4_2_1.html",
    52: "privacy/mod4_2_2.html",           53: "privacy/mod4_2_3.html",           54: "privacy/mod4_2_4.html",               55: "privacy/mod4_2_5.html",
    56: "privacy/mod4_3_0.html",           57: "privacy/mod4_review.html",        58: "https://jrvidal.github.io/aes-demo/", 59: "https://cryptii.com/",
    60: "privacy/mod4_kc.html",            61: "privacy/mod4_cs.html",            62: "privacy/mod4_ref.html",               63: "contact.html"
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

