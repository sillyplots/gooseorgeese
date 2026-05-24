import { describe, it, expect } from 'vitest';
import { cleanTitle } from './main.js';

describe('cleanTitle', () => {
    it('decodes HTML entities', () => {
        expect(cleanTitle('Rock &amp; Roll')).toBe('Rock & Roll');
        expect(cleanTitle('Don&#39;t Stop')).toBe("Don't Stop");
        expect(cleanTitle('The &quot;Best&quot; Song')).toBe('The "Best" Song');
        // Because of quote stripping, 'The "Best" Song' becomes 'The "Best" Song'
        // Wait, quote stripping: "Remove surrounding quotes if present"
        // Let's test just HTML entity
        expect(cleanTitle('&quot;Quoted&quot;')).toBe('Quoted');
    });

    it('removes standard suffixes', () => {
        expect(cleanTitle('Hungersite (Official Video)')).toBe('Hungersite');
        expect(cleanTitle('Arcadia (Official Music Video)')).toBe('Arcadia');
        expect(cleanTitle('Creatures (Official Audio)')).toBe('Creatures');
        expect(cleanTitle('Hot Tea (Official Visualizer)')).toBe('Hot Tea');
        expect(cleanTitle('Tumble (Official Lyric Video)')).toBe('Tumble');
        expect(cleanTitle('Slow Ready (Live)')).toBe('Slow Ready');
        expect(cleanTitle('Wysteria Lane (Live on KEXP)')).toBe('Wysteria Lane');
        expect(cleanTitle('Arrow [4K]')).toBe('Arrow');
        expect(cleanTitle('Dripfield [Full Album]')).toBe('Dripfield');
    });

    it('removes band prefixes', () => {
        expect(cleanTitle('Goose - Hungersite')).toBe('Hungersite');
        expect(cleanTitle('Goose: Arcadia')).toBe('Arcadia');
        expect(cleanTitle('Goose Hot Tea')).toBe('Hot Tea');
        expect(cleanTitle('Geese - Cowboy Nudes')).toBe('Cowboy Nudes');
        expect(cleanTitle('Geese: 2122')).toBe('2122');
        expect(cleanTitle('Geese Low Era')).toBe('Low Era');
        expect(cleanTitle('Goose-Arcadia')).toBe('Arcadia');
        expect(cleanTitle('Geese-2122')).toBe('2122');
    });

    it('removes specific show patterns', () => {
        expect(cleanTitle('Saturday Sessions: Goose performs Hungersite')).toBe('Hungersite');
        expect(cleanTitle('Arcadia | The Tonight Show Starring Jimmy Fallon')).toBe('Arcadia');
        expect(cleanTitle('Creatures | From The Basement')).toBe('Creatures');
        expect(cleanTitle('Official TGR x Goose Tumble')).toBe('Tumble');
        expect(cleanTitle('Official TGR x Goose Tumble Music Video')).toBe('Tumble');
    });

    it('removes trailing dates/locations', () => {
        expect(cleanTitle('Hungersite - 12/31/22 Cincinnati, OH')).toBe('Hungersite');
        expect(cleanTitle('Arcadia - 06/25/23 Chicago, IL')).toBe('Arcadia');
    });

    it('removes surrounding quotes', () => {
        expect(cleanTitle('"Hungersite"')).toBe('Hungersite');
        expect(cleanTitle('""Arcadia""')).toBe('"Arcadia"');
    });

    it('handles combinations of modifications', () => {
        expect(cleanTitle('Goose - "Hungersite" (Live on KEXP) - 10/12/21 Seattle, WA')).toBe('Hungersite');
        expect(cleanTitle('Saturday Sessions: Goose performs "Arcadia" (Official Video)')).toBe('Arcadia');
    });

    it('trims whitespace', () => {
        expect(cleanTitle('  Hungersite  ')).toBe('Hungersite');
    });
});
