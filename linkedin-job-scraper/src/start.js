window.onload = async function () {
    setInterval(injectButton, 2000);
}

async function injectButton() {
    if (
        window.location.href.includes("/in/")
    )
    {
        let bodyEle = document.body;

        if (bodyEle != null) {
            if (bodyEle.querySelector(".INJECT_BTN") == null) {
                let ourElement = document.createElement("INJECT_ELEMENT");
                ourElement.setAttribute("id", "INJECT_BTN_ID");

                ourElement.setAttribute(
                    "style",
                    `z-index: 999999999999; top: 70%; right: 0; cursor: pointer; position: absolute;`
                );

                ourElement.innerHTML = `<img style="max-width: 40px;" class="INJECT_BTN" src="${chrome.runtime.getURL(
                    "assets/images/web.svg"
                )}">`;
                bodyEle.appendChild(ourElement);

                elel = document.querySelector("#INJECT_BTN_ID");
                elel.addEventListener('mouseenter', () => {
                    ourElement.style.transition = 'right 0.3s ease-in-out 0.3s';
                    ourElement.style.right = '30px';
                
                    elel.addEventListener('mouseleave', () => {
                        ourElement.style.transition = 'right 0.3s ease-in-out';
                        ourElement.style.right = '5px';
                    });
                });

                imgEle = document.querySelector(".INJECT_BTN");
                getLinkedInCookies()
                imgEle.addEventListener("click", function () {
                    getUserDetails();
                })
            }
        }
    }
}

// function to get the linkedin cookies
function getLinkedInCookies() {
    chrome.runtime.sendMessage({ action: "getLinkedInCookies" }, function (response) {
        if (response.cookies) {
            localStorage.setItem('li_at', response.cookies.li_at);
            localStorage.setItem('JSESSIONID', response.cookies.JSESSIONID);
        } else {
            console.log("Cookies not found.");
        }
    });
}

function getUserDetails() {
    let employeeName = window.document.querySelector('[class*="text-heading-xlarge"]').textContent;
    window.document.querySelectorAll('[class*="pvs-header__title"] [aria-hidden="true"]').forEach((e) => {
        if (e.textContent == "Experience") {
            let mainExperienceDiv = e.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement;
            let companyUrl = mainExperienceDiv.querySelector('[data-field="experience_company_logo"]').href
            const li_atCookie = localStorage.getItem('li_at');
            const jsessionidCookie = localStorage.getItem('JSESSIONID');

            let jsonData = {
                "li_at": li_atCookie,
                "JSESSIONID": jsessionidCookie,
                "companyUrl": getCompanyId(companyUrl),
                "employeeName": employeeName
            };
            console.log("🚀 ~ window.document.querySelectorAll ~ jsonData:", jsonData)

            // send message to background.js
            chrome.runtime.sendMessage({ action: "callApi", data: jsonData }, function (response) {
                console.log("🚀 ~ response:", response)
            });
            showToaster("success", "Scraping has been successfully started");
        }
    })
    function showToaster(type, message) {
        console.log("showToaster");
        Swal.fire({
            position: "center",
            icon: type,
            title: message,
            showConfirmButton: false,
            timer: 2500,
        });
    }
    function getCompanyId(url) {
        const regex = /\/company\/(\d+)\//;
        const match = url.match(regex);
        return match ? match[1] : null;
    }
}
