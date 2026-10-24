import {Glyph as OriginalGlyph, type GlyphName as OriginalName} from '../../components/Glyph';
export {CheckMark} from '../../components/Glyph';
export type GlyphName = OriginalName | 'back' | 'gamepad' | 'av';
export function Glyph({name}:{name:GlyphName}) {
 if(name !== 'back' && name !== 'gamepad' && name !== 'av')return <OriginalGlyph name={name}/>;
 return <svg class="tile__glyph" viewBox="0 0 24 24" aria-hidden="true">{name==='back'?<path d="m14.5 5-7 7 7 7"/>:name==='gamepad'?<path d="M7 6h10c2 0 3 2 3.5 5l1 5c.5 3-2 4-4 1l-1.5-2H8l-1.5 2c-2 3-4.5 2-4-1l1-5C4 8 5 6 7 6ZM7 9v4M5 11h4M16 10h.1M18 12h.1"/>:<path d="M4 5h5v8H4zM6.5 13v6M15 5h5v8h-5zM17.5 13v6M4 9h5M15 9h5"/>}</svg>;
}
