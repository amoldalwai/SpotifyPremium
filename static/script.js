const searchInput = document.getElementById('searchInput');
const providerSelect = document.getElementById('providerSelect');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');

// Full Page Player Elements
const fullpagePlayer = document.getElementById('fullpagePlayer');
const playerBackground = document.getElementById('playerBackground');
const backBtn = document.getElementById('backBtn');
const fullPlayerImage = document.getElementById('fullPlayerImage');
const fullPlayerTitle = document.getElementById('fullPlayerTitle');
const fullPlayerArtist = document.getElementById('fullPlayerArtist');
const fullPlayerProvider = document.getElementById('fullPlayerProvider');
const progressFill = document.getElementById('progressFill');
const progressThumb = document.getElementById('progressThumb');
const fullCurrentTime = document.getElementById('fullCurrentTime');
const fullTotalTime = document.getElementById('fullTotalTime');
const playPauseBtnFull = document.getElementById('playPauseBtnFull');
const prevBtnFull = document.getElementById('prevBtnFull');
const nextBtnFull = document.getElementById('nextBtnFull');
const shuffleBtnFull = document.getElementById('shuffleBtnFull');
const repeatBtnFull = document.getElementById('repeatBtnFull');
const likeBtnFull = document.getElementById('likeBtnFull');
const volumeBtnFull = document.getElementById('volumeBtnFull');

// Mini Player Elements
const miniPlayer = document.getElementById('miniPlayer');
const miniImage = document.getElementById('miniImage');
const miniTitle = document.getElementById('miniTitle');
const miniArtist = document.getElementById('miniArtist');
const miniPlayPauseBtn = document.getElementById('miniPlayPauseBtn');
const miniPrevBtn = document.getElementById('miniPrevBtn');
const miniNextBtn = document.getElementById('miniNextBtn');
const expandBtn = document.getElementById('expandBtn');
const miniProgressBar = document.getElementById('miniProgressBar');

// Audio Element
const audioPlayer = document.getElementById('audioPlayer');

let currentTrack = null;
let isPlaying = false;
let isLiked = false;

// Search functionality
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

async function performSearch() {
    const query = searchInput.value.trim();
    const provider = providerSelect.value;
    
    if (!query) {
        return;
    }
    
    loading.style.display = 'flex';
    searchResults.innerHTML = '';
    if (emptyState) emptyState.style.display = 'none';
    
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}&provider=${provider}`);
        const data = await response.json();
        
        loading.style.display = 'none';
        
        if (data.error) {
            showEmptyState('Error: ' + data.error);
            return;
        }
        
        if (data.length === 0) {
            showEmptyState('No results found');
            return;
        }
        
        displayResults(data);
    } catch (error) {
        loading.style.display = 'none';
        showEmptyState('Error searching. Please try again.');
        console.error('Search error:', error);
    }
}

function showEmptyState(message) {
    if (emptyState) {
        emptyState.style.display = 'flex';
        emptyState.querySelector('p').textContent = message;
    }
}

function displayResults(data) {
    searchResults.innerHTML = '';
    
    // Handle flat array of results
    if (Array.isArray(data) && data.length > 0) {
        data.forEach((item, index) => {
            const resultItem = createResultItem(item);
            resultItem.style.animationDelay = `${index * 0.05}s`;
            searchResults.appendChild(resultItem);
        });
    }
}

function createResultItem(item) {
    const div = document.createElement('div');
    div.className = 'result-item';
    
    const img = document.createElement('img');
    img.src = item.image || 'https://via.placeholder.com/200?text=No+Image';
    img.alt = item.title;
    img.onerror = function() {
        this.src = 'https://via.placeholder.com/200?text=No+Image';
    };
    
    const info = document.createElement('div');
    info.className = 'result-info';
    
    const title = document.createElement('h3');
    title.textContent = item.title;
    
    const artist = document.createElement('p');
    artist.textContent = item.artist || 'Unknown Artist';
    
    info.appendChild(title);
    info.appendChild(artist);
    
    if (item.duration) {
        const duration = document.createElement('p');
        duration.className = 'duration';
        duration.textContent = formatDuration(item.duration);
        info.appendChild(duration);
    }
    
    div.appendChild(img);
    div.appendChild(info);
    
    // Add play functionality
    div.addEventListener('click', () => playTrack(item));
    
    return div;
}

async function playTrack(track) {
    currentTrack = track;
    
    // Update Mini Player UI
    miniImage.src = track.image || 'https://via.placeholder.com/80?text=No+Image';
    miniImage.onerror = function() {
        this.src = 'https://via.placeholder.com/80?text=No+Image';
    };
    miniTitle.textContent = track.title;
    miniArtist.textContent = track.artist || 'Unknown Artist';
    
    // Update Full Player UI
    fullPlayerImage.src = track.image || 'https://via.placeholder.com/400?text=No+Image';
    fullPlayerImage.onerror = function() {
        this.src = 'https://via.placeholder.com/400?text=No+Image';
    };
    fullPlayerTitle.textContent = track.title;
    fullPlayerArtist.textContent = track.artist || 'Unknown Artist';
    fullPlayerProvider.textContent = track.provider;
    
    // Set background
    if (track.image) {
        playerBackground.style.backgroundImage = `url(${track.image})`;
    }
    
    // Show mini player and expand to full view
    miniPlayer.style.display = 'flex';
    fullpagePlayer.style.display = 'flex';
    
    try {
        // Get stream URL from backend
        const response = await fetch(`/stream?id=${encodeURIComponent(track.id)}&provider=${track.provider}`);
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        if (data.url) {
            audioPlayer.src = data.url;
            audioPlayer.play().then(() => {
                isPlaying = true;
                updatePlayButtons();
            }).catch(err => {
                console.error('Play error:', err);
                alert('Error playing track. The stream may have expired. Try searching again.');
            });
        } else {
            alert('Could not play this track');
        }
    } catch (error) {
        console.error('Play error:', error);
        alert('Error playing track');
    }
}

// Player View Toggle
backBtn.addEventListener('click', () => {
    fullpagePlayer.style.display = 'none';
});

expandBtn.addEventListener('click', () => {
    fullpagePlayer.style.display = 'flex';
});

// Click on mini player track info to expand
document.querySelector('.mini-player-track').addEventListener('click', () => {
    fullpagePlayer.style.display = 'flex';
});

// Play/Pause functionality - Full Player
playPauseBtnFull.addEventListener('click', togglePlayPause);

// Play/Pause functionality - Mini Player
miniPlayPauseBtn.addEventListener('click', togglePlayPause);

function togglePlayPause() {
    if (isPlaying) {
        audioPlayer.pause();
        isPlaying = false;
    } else {
        audioPlayer.play();
        isPlaying = true;
    }
    updatePlayButtons();
}

function updatePlayButtons() {
    const fullIcon = playPauseBtnFull.querySelector('i');
    const miniIcon = miniPlayPauseBtn.querySelector('i');
    
    if (isPlaying) {
        fullIcon.className = 'fas fa-pause';
        miniIcon.className = 'fas fa-pause';
    } else {
        fullIcon.className = 'fas fa-play';
        miniIcon.className = 'fas fa-play';
    }
}

// Audio player events
audioPlayer.addEventListener('loadedmetadata', () => {
    fullTotalTime.textContent = formatTime(audioPlayer.duration);
});

audioPlayer.addEventListener('timeupdate', () => {
    const currentTimeValue = audioPlayer.currentTime;
    const duration = audioPlayer.duration;
    const progressPercent = (currentTimeValue / duration) * 100;
    
    // Update full player progress
    fullCurrentTime.textContent = formatTime(currentTimeValue);
    progressFill.style.width = progressPercent + '%';
    progressThumb.style.left = progressPercent + '%';
    
    // Update mini player progress
    miniProgressBar.style.width = progressPercent + '%';
});

audioPlayer.addEventListener('play', () => {
    isPlaying = true;
    updatePlayButtons();
});

audioPlayer.addEventListener('pause', () => {
    isPlaying = false;
    updatePlayButtons();
});

audioPlayer.addEventListener('ended', () => {
    isPlaying = false;
    updatePlayButtons();
});

// Progress bar click to seek - Full Player
document.querySelector('.progress-bar-full').addEventListener('click', (e) => {
    const progressBar = e.currentTarget;
    const clickX = e.offsetX;
    const width = progressBar.offsetWidth;
    const duration = audioPlayer.duration;
    
    audioPlayer.currentTime = (clickX / width) * duration;
});

// Volume control - Full Player
let isMuted = false;
let previousVolume = 1;

volumeBtnFull.addEventListener('click', () => {
    if (isMuted) {
        audioPlayer.volume = previousVolume;
        volumeBtnFull.querySelector('i').className = 'fas fa-volume-up';
        isMuted = false;
    } else {
        previousVolume = audioPlayer.volume;
        audioPlayer.volume = 0;
        volumeBtnFull.querySelector('i').className = 'fas fa-volume-mute';
        isMuted = true;
    }
});

// Like button - Full Player
likeBtnFull.addEventListener('click', () => {
    isLiked = !isLiked;
    const icon = likeBtnFull.querySelector('i');
    
    if (isLiked) {
        icon.className = 'fas fa-heart';
        likeBtnFull.classList.add('active');
    } else {
        icon.className = 'far fa-heart';
        likeBtnFull.classList.remove('active');
    }
});

// Control buttons - Full Player
shuffleBtnFull.addEventListener('click', () => {
    shuffleBtnFull.classList.toggle('active');
    console.log('Shuffle toggled');
});

prevBtnFull.addEventListener('click', () => {
    console.log('Previous track');
});

nextBtnFull.addEventListener('click', () => {
    console.log('Next track');
});

repeatBtnFull.addEventListener('click', () => {
    repeatBtnFull.classList.toggle('active');
    console.log('Repeat toggled');
});

// Control buttons - Mini Player
miniPrevBtn.addEventListener('click', () => {
    console.log('Previous track');
});

miniNextBtn.addEventListener('click', () => {
    console.log('Next track');
});

// Format time helper
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatDuration(seconds) {
    const secs = parseInt(seconds);
    if (isNaN(secs)) return '';
    
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins}:${remainingSecs.toString().padStart(2, '0')}`;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    
    switch(e.key) {
        case ' ':
            e.preventDefault();
            playPauseBtn.click();
            break;
        case 'ArrowLeft':
            audioPlayer.currentTime = Math.max(0, audioPlayer.currentTime - 5);
            break;
        case 'ArrowRight':
            audioPlayer.currentTime = Math.min(audioPlayer.duration, audioPlayer.currentTime + 5);
            break;
    }
});

