// Get all the banner elements
const getBanners = () => {
    return document.querySelectorAll('#banners .banner');
};

let banners = getBanners();
document.onload = () => {
    banners = getBanners();
};

let currentBannerIndex = 0;
let totalBanners = banners.length;
let nextBannerIndex = (currentBannerIndex + 1) % totalBanners;

// Hide all banners except the first one
for (let i = 1; i < totalBanners; i++) {
    banners[i].style.display = 'none';
}

// Function to show the next banner
function showNextBanner() {
    banners[currentBannerIndex].style.opacity = 0;
    setTimeout(() => {
        nextBannerIndex = (currentBannerIndex + 1) % totalBanners;
        banners[nextBannerIndex].style.display = 'block';
        banners[currentBannerIndex].style.display = 'none';
        banners[nextBannerIndex].style.opacity = 1;

        currentBannerIndex = nextBannerIndex;
    }, 470);
}

// Function to show the previous banner
function showPreviousBanner() {
    banners[currentBannerIndex].style.opacity = 0;
    banners[currentBannerIndex].style.visibility = 'collapse';
    banners[currentBannerIndex].style.visibility = 'visible';
    banners[currentBannerIndex].style.opacity = 1;
    setTimeout(() => {
        banners[currentBannerIndex].style.display = 'none';

        currentBannerIndex = (currentBannerIndex - 1 + totalBanners) % totalBanners;
        banners[currentBannerIndex].style.display = 'block';
        banners[currentBannerIndex].style.opacity = 1;
    }, 490);
}

//setTimeout(function() { banners = getBanners(); }, 200);

// Set interval to automatically change banners every 5 seconds
setInterval(showNextBanner, 5000);

