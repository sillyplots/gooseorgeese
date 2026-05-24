import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

vi.mock('./songs.js', () => ({
    songs: [
        { title: 'Song 1', artist: 'Goose', youtubeId: '1', duration: 10, totalDuration: 100, startTime: 0 },
        { title: 'Song 2', artist: 'Geese', youtubeId: '2', duration: 10, totalDuration: 100, startTime: 0 }
    ]
}));

describe('Main logic', () => {
    let windowYTBackup;
    let mockPlayerInstance;
    let main;
    let mathRandomBackup;

    beforeEach(async () => {
        vi.resetModules();
        window.songsData = [
            { title: 'Song 1', artist: 'Goose', youtubeId: '1', duration: 10, totalDuration: 100, startTime: 0 },
            { title: 'Song 2', artist: 'Geese', youtubeId: '2', duration: 10, totalDuration: 100, startTime: 0 }
        ];
        document.body.innerHTML = `
            <div id="app"></div>
            <button id="play-btn"></button>
            <div id="status-message"></div>
            <div id="score">0</div>
            <div id="streak">0</div>
            <div class="game-container"></div>
            <div id="prize-container" class="prize-container hidden">
                <a href="#" class="prize-link"></a>
            </div>
            <button class="choice-btn goose" data-artist="Goose"></button>
            <button class="choice-btn geese" data-artist="Geese"></button>
            <script></script>
        `;

        windowYTBackup = window.YT;

        mockPlayerInstance = {
            playVideo: vi.fn(),
            pauseVideo: vi.fn(),
            cueVideoById: vi.fn(),
            setVolume: vi.fn()
        };

        window.YT = {
            Player: vi.fn().mockImplementation(function(id, options) {
                this.options = options;
                Object.assign(this, mockPlayerInstance);
            }),
            PlayerState: { ENDED: 0 }
        };

        mathRandomBackup = Math.random;

        vi.useFakeTimers();

        main = await import('./main.js');
    });

    afterEach(() => {
        vi.useRealTimers();
        window.YT = windowYTBackup;
        Math.random = mathRandomBackup;
    });

    describe('Initialization and YouTube Player Setup', () => {
        it('initializes the YouTube player on API ready', () => {
            expect(window.onYouTubeIframeAPIReady).toBeDefined();
            window.onYouTubeIframeAPIReady();

            expect(window.YT.Player).toHaveBeenCalledTimes(1);
            expect(window.YT.Player).toHaveBeenCalledWith('audio-container', expect.any(Object));
        });

        it('enables play button and updates status when player is ready', () => {
            window.onYouTubeIframeAPIReady();
            const playerArgs = window.YT.Player.mock.calls[0];
            const playerOptions = playerArgs[1];

            // Simulate onReady event
            playerOptions.events.onReady({
                target: {
                    setVolume: vi.fn()
                }
            });

            const playBtn = document.getElementById('play-btn');
            const statusMsg = document.getElementById('status-message');

            expect(playBtn.disabled).toBe(false);
            expect(statusMsg.textContent).toBe('Ready to play!');
        });
    });

    describe('Playing and stopping songs', () => {
        beforeEach(() => {
            window.onYouTubeIframeAPIReady();
            const playerArgs = window.YT.Player.mock.calls[0];
            const playerOptions = playerArgs[1];
            playerOptions.events.onReady({
                target: { setVolume: vi.fn() }
            });
            // Advance timers to clear the initial interval
            vi.advanceTimersByTime(500);
        });

        it('plays a song when play button is clicked', () => {
            const playBtn = document.getElementById('play-btn');
            playBtn.click();

            expect(mockPlayerInstance.cueVideoById).toHaveBeenCalled();
            expect(mockPlayerInstance.playVideo).toHaveBeenCalled();

            const statusMsg = document.getElementById('status-message');
            expect(statusMsg.textContent).toBe('Name that fowl foursome!');
        });

        it('stops playing when play button is clicked while playing', () => {
            const playBtn = document.getElementById('play-btn');
            playBtn.click(); // play

            expect(mockPlayerInstance.playVideo).toHaveBeenCalled();

            playBtn.click(); // pause
            expect(mockPlayerInstance.pauseVideo).toHaveBeenCalled();
        });

        it('automatically stops playing after duration', () => {
            const playBtn = document.getElementById('play-btn');
            playBtn.click(); // play

            expect(mockPlayerInstance.playVideo).toHaveBeenCalled();

            // Fast-forward time by duration (10s * 1000ms = 10000ms)
            vi.advanceTimersByTime(10000);

            expect(mockPlayerInstance.pauseVideo).toHaveBeenCalled();
        });
    });

    describe('Guessing logic', () => {
        beforeEach(() => {
            // Force Math.random to return 0.1 so 'Goose' is always selected
            Math.random = vi.fn().mockReturnValue(0.1);

            window.onYouTubeIframeAPIReady();
            const playerArgs = window.YT.Player.mock.calls[0];
            const playerOptions = playerArgs[1];
            playerOptions.events.onReady({
                target: { setVolume: vi.fn() }
            });
            vi.advanceTimersByTime(500);

            const playBtn = document.getElementById('play-btn');
            playBtn.click();
        });

        it('handles correct guesses', () => {
            const gooseBtn = document.querySelector('.choice-btn.goose');
            gooseBtn.click();

            const score = document.getElementById('score');
            const streak = document.getElementById('streak');
            const statusMsg = document.getElementById('status-message');

            expect(score.textContent).toBe('10');
            expect(streak.textContent).toBe('1');
            expect(statusMsg.textContent).toContain('Song 1');
            expect(mockPlayerInstance.pauseVideo).toHaveBeenCalled();
        });

        it('handles incorrect guesses', () => {
            const geeseBtn = document.querySelector('.choice-btn.geese');
            geeseBtn.click();

            const score = document.getElementById('score');
            const streak = document.getElementById('streak');
            const statusMsg = document.getElementById('status-message');

            expect(score.textContent).toBe('0');
            expect(streak.textContent).toBe('0');
            expect(statusMsg.textContent).toContain('Wrong'); // Should be a fail message
            expect(statusMsg.textContent).toContain('Song 1');
        });

        it('shows prize container on 3 streak', () => {
            const gooseBtn = document.querySelector('.choice-btn.goose');

            // Guess correctly 3 times
            gooseBtn.click();
            vi.advanceTimersByTime(2500);
            document.getElementById('play-btn').click(); // Play next

            gooseBtn.click();
            vi.advanceTimersByTime(2500);
            document.getElementById('play-btn').click(); // Play next

            gooseBtn.click();

            const streak = document.getElementById('streak');
            expect(streak.textContent).toBe('3');

            vi.advanceTimersByTime(2500);

            const prizeContainer = document.getElementById('prize-container');
            expect(prizeContainer.classList.contains('hidden')).toBe(false);
        });
    });
});
