import type {ComponentChildren} from 'preact';
import {useLayoutEffect, useRef} from 'preact/hooks';
import {applyTokens} from '../theme/tokens';

/** Accepted presentation tokens belong to this layer, never to upstream screens. */
export function Layer({children,enabled=true}:{children:ComponentChildren;enabled?:boolean}) {
 const root=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{if(root.current)applyTokens(root.current);},[enabled]);
 return enabled?<div class="matched-ui" ref={root}>{children}</div>:<>{children}</>;
}
