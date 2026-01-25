// Audio State
let audioEnabled = false;
let tickSynth;
let chimeSynth;
let hourStrikeSynth;
let lastSecond = -1;

// Melody: Westminster Quarters (Key of E) - Quarter 4 (Full Hour)
// E4, G#4, F#4, B3 | E4, F#4, G#4, E4 | G#4, E4, F#4, B3 | B3, F#4, G#4, E4
// Simplified for V1 (Just the last phrase + strike)
const westminsterMelody = [
    { note: "B3", time: 0 }, { note: "F#4", time: 0.5 }, { note: "G#4", time: 1.0 }, { note: "E4", time: 1.5 }
];

async function initAudio() {
    console.log("Initializing audio...");
    try {
        await Tone.start();
        console.log("AudioContext started");
        
        // Resume context if suspended (browser policy fallback)
        if (Tone.context.state !== 'running') {
            await Tone.context.resume();
        }

        // Tick Sound (Crisper Mechanical Click)
        // Using a high-pass filtered noise burst + sharp sine for that "escapement" snap
        tickSynth = new Tone.MembraneSynth({
            pitchDecay: 0.01,
            octaves: 6, 
            oscillator: { type: "square4" }, // Square wave for more harmonics (crispy)
            envelope: { attack: 0.001, decay: 0.03, sustain: 0, release: 0.01 } // Very short
        }).toDestination();
        tickSynth.volume.value = -2; // Loud and proud

        // Chime Melody Synth (Bell-like)
        chimeSynth = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "sine" },
            envelope: { attack: 0.01, decay: 1, sustain: 0.1, release: 3 }
        }).toDestination();
        chimeSynth.volume.value = -5;

        // Hour Strike (Deep Gong)
        hourStrikeSynth = new Tone.MetalSynth({
            frequency: 200,
            envelope: { attack: 0.001, decay: 1.4, release: 0.2 },
            harmonicity: 5.1,
            modulationIndex: 32,
            resonance: 4000,
            octaves: 1.5
        }).toDestination();
        hourStrikeSynth.volume.value = 0;
        
        audioEnabled = true;
        console.log("Audio enabled");
    } catch (e) {
        console.error("Audio init failed:", e);
        alert("Audio initialization failed. Please check console.");
    }
}

// Visual Logic
function updateClock() {
    const now = new Date();
    
    const seconds = now.getSeconds();
    const minutes = now.getMinutes();
    const hours = now.getHours();

    // Prevent double-triggering or skipping if setInterval jitters
    if (seconds === lastSecond) return;
    lastSecond = seconds;

    const secondDegrees = ((seconds / 60) * 360);
    const minuteDegrees = ((minutes / 60) * 360) + ((seconds/60)*6);
    const hourDegrees = ((hours / 12) * 360) + ((minutes/60)*30);

    const secondHand = document.querySelector('#second');
    const minuteHand = document.querySelector('#minute');
    const hourHand = document.querySelector('#hour');

    secondHand.style.transform = `translateX(-50%) rotate(${secondDegrees}deg)`;
    minuteHand.style.transform = `translateX(-50%) rotate(${minuteDegrees}deg)`;
    hourHand.style.transform = `translateX(-50%) rotate(${hourDegrees}deg)`;

    // Audio Logic
    if (audioEnabled) {
        // Tick every second (alternate pitch slightly for tick-tock feel)
        // Higher pitch for "crisp" sound (C5/G4 instead of C2/G1)
        const note = seconds % 2 === 0 ? "C5" : "G4";
        // Use explicit time duration (0.05s) to avoid envelope clipping
        tickSynth.triggerAttackRelease(note, 0.05);

        // Check for Hour Chime
        if (minutes === 0 && seconds === 0) {
            playHourChime(hours);
        }
    }
}

function playHourChime(hours) {
    const strikeCount = hours % 12 || 12;
    const now = Tone.now();
    
    console.log(`Chiming for ${hours} hours (${strikeCount} strikes)`);

    // 1. Play Melody (Pre-roll)
    // Simple 4-note cadence before the strike
    let melodyDuration = 0;
    westminsterMelody.forEach((part) => {
        chimeSynth.triggerAttackRelease(part.note, "4n", now + part.time);
        melodyDuration = Math.max(melodyDuration, part.time + 0.5); // Track end time
    });

    // 2. Schedule strikes after melody
    const strikeStartTime = now + melodyDuration + 1.0; // 1s buffer
    for (let i = 0; i < strikeCount; i++) {
        hourStrikeSynth.triggerAttackRelease("E3", "1n", strikeStartTime + (i * 2.5)); // Slower, heavier strikes
    }
}

// Start Button Handler
document.getElementById('start-btn').addEventListener('click', async () => {
    const btn = document.getElementById('start-btn');
    btn.textContent = "Winding...";
    
    await initAudio();
    
    document.getElementById('start-overlay').classList.add('hidden');
});

// Run loop
setInterval(updateClock, 100); // Run faster to catch second changes precisely
updateClock();
