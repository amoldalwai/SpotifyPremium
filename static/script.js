const searchInput = document.getElementById('searchInput');
const providerSelect = document.getElementById('providerSelect');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const playerContainer = document.getElementById('playerContainer');
const audioPlayer = document.getElementById('audioPlayer');
const currentImage = document.getElementById('currentImage');
const currentTitle = document.getElementById('currentTitle');
const currentArtist = document.getElementById('currentArtist');
const currentProvider = document.getElementById('currentProvider');
const progressBar = document.getElementById('progressBar');
const currentTime = document.getElementById('currentTime');
const totalTime = document.getElementById('totalTime');
const playPauseBtn = document.getElementById('playPauseBtn');
const volumeSlider = document.getElementById('volumeSlider');
const volumeBtn = document.getElementById('volumeBtn');
const likeBtn = document.querySelector('.like-btn');

let currentTrack = null;
let isPlaying = false;

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
    
    // Update UI
    currentImage.src = track.image || 'https://via.placeholder.com/80?text=No+Image';
    currentImage.onerror = function() {
        this.src = 'https://via.placeholder.com/80?text=No+Image';
    };
    currentTitle.textContent = track.title;
    currentArtist.textContent = track.artist || 'Unknown Artist';
    currentProvider.textContent = track.provider;
    currentProvider.className = `provider-badge ${track.provider}`;
    
    playerContainer.style.display = 'grid';
    
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
                updatePlayButton();
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

// Play/Pause functionality
playPauseBtn.addEventListener('click', () => {
    if (isPlaying) {
        audioPlayer.pause();
        isPlaying = false;
    } else {
        audioPlayer.play();
        isPlaying = true;
    }
    updatePlayButton();
});

function updatePlayButton() {
    const icon = playPauseBtn.querySelector('i');
    if (isPlaying) {
        icon.className = 'fas fa-pause';
    } else {
        icon.className = 'fas fa-play';
    }
}

// Audio player events
audioPlayer.addEventListener('loadedmetadata', () => {
    totalTime.textContent = formatTime(audioPlayer.duration);
    progressBar.max = audioPlayer.duration;
});

audioPlayer.addEventListener('timeupdate', () => {
    currentTime.textContent = formatTime(audioPlayer.currentTime);
    progressBar.value = audioPlayer.currentTime;
});

audioPlayer.addEventListener('play', () => {
    isPlaying = true;
    updatePlayButton();
});

audioPlayer.addEventListener('pause', () => {
    isPlaying = false;
    updatePlayButton();
});

audioPlayer.addEventListener('ended', () => {
    isPlaying = false;
    updatePlayButton();
});

progressBar.addEventListener('input', () => {
    audioPlayer.currentTime = progressBar.value;
});

// Volume control
volumeSlider.addEventListener('input', () => {
    audioPlayer.volume = volumeSlider.value / 100;
    updateVolumeIcon();
});

volumeBtn.addEventListener('click', () => {
    if (audioPlayer.volume > 0) {
        audioPlayer.volume = 0;
        volumeSlider.value = 0;
    } else {
        audioPlayer.volume = 1;
        volumeSlider.value = 100;
    }
    updateVolumeIcon();
});

function updateVolumeIcon() {
    const icon = volumeBtn.querySelector('i');
    const volume = audioPlayer.volume;
    
    if (volume === 0) {
        icon.className = 'fas fa-volume-mute';
    } else if (volume < 0.5) {
        icon.className = 'fas fa-volume-down';
    } else {
        icon.className = 'fas fa-volume-up';
    }
}

// Like button
likeBtn.addEventListener('click', () => {
    likeBtn.classList.toggle('active');
});

// Shuffle, prev, next, repeat buttons (placeholder functionality)
document.getElementById('shuffleBtn').addEventListener('click', () => {
    console.log('Shuffle clicked');
});

document.getElementById('prevBtn').addEventListener('click', () => {
    console.log('Previous clicked');
});

document.getElementById('nextBtn').addEventListener('click', () => {
    console.log('Next clicked');
});

document.getElementById('repeatBtn').addEventListener('click', () => {
    console.log('Repeat clicked');
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

