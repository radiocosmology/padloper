import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Button, ButtonGroup, Chip, CircularProgress, Stack, Typography,
} from '@mui/material';
import { withBase } from './paths.js';
import ErrorMessage from './ErrorMessage.js';

const MIN_SCALE = 0.05;
const MAX_SCALE = 10;
const WHEEL_STEP = 1.15;
const BUTTON_STEP = 1.25;

/** Natural pixel size of an inline SVG from its width/height attributes
 *  (Graphviz writes them in points). */
function svgPixelSize(svgEl) {
    const toPx = (value) => {
        if (!value) return 0;
        const n = parseFloat(value);
        if (Number.isNaN(n)) return 0;
        return value.trim().endsWith('pt') ? (n * 96) / 72 : n;
    };
    let w = toPx(svgEl.getAttribute('width'));
    let h = toPx(svgEl.getAttribute('height'));
    if ((!w || !h) && svgEl.viewBox && svgEl.viewBox.baseVal) {
        w = w || svgEl.viewBox.baseVal.width;
        h = h || svgEl.viewBox.baseVal.height;
    }
    return { w, h };
}

/**
 * Whole-system diagram. The server renders the inventory to SVG with Graphviz
 * (/api/system_diagram.svg); this page inlines it with drag-to-pan and
 * wheel-to-zoom. Clicking a component box opens that component's page; the
 * legend chips (from /api/system_diagram.json) highlight one type at a time.
 */
export default function SystemDiagram() {
    const navigate = useNavigate();
    const [svg, setSvg] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [scalePct, setScalePct] = useState(100);
    const [legend, setLegend] = useState(null);       // {types, components, connections}
    const [highlight, setHighlight] = useState(null); // colour of the highlighted type
    const viewportRef = useRef(null);
    const contentRef = useRef(null);
    const view = useRef({ x: 0, y: 0, scale: 1 });
    const drag = useRef(null);
    const moved = useRef(false);

    const applyTransform = useCallback(() => {
        const v = view.current;
        if (contentRef.current) {
            contentRef.current.style.transform =
                `translate(${v.x}px, ${v.y}px) scale(${v.scale})`;
        }
    }, []);

    const apply = useCallback(() => {
        applyTransform();
        setScalePct(Math.round(view.current.scale * 100));
    }, [applyTransform]);

    /** Zoom by `factor`, keeping the viewport point (cx, cy) fixed. */
    const zoomBy = useCallback((factor, cx, cy) => {
        const v = view.current;
        const next = Math.min(MAX_SCALE, Math.max(MIN_SCALE, v.scale * factor));
        const f = next / v.scale;
        if (cx === undefined || cy === undefined) {
            const vp = viewportRef.current;
            cx = vp ? vp.clientWidth / 2 : 0;
            cy = vp ? vp.clientHeight / 2 : 0;
        }
        v.x = cx - (cx - v.x) * f;
        v.y = cy - (cy - v.y) * f;
        v.scale = next;
        apply();
    }, [apply]);

    /** Scale the drawing to fit the viewport and centre it. */
    const fit = useCallback(() => {
        const vp = viewportRef.current;
        const el = contentRef.current && contentRef.current.querySelector('svg');
        if (!vp || !el) return;
        const { w, h } = svgPixelSize(el);
        if (!w || !h || !vp.clientWidth || !vp.clientHeight) return;
        const scale = Math.min(vp.clientWidth / w, vp.clientHeight / h) * 0.97;
        view.current = {
            scale,
            x: (vp.clientWidth - w * scale) / 2,
            y: (vp.clientHeight - h * scale) / 2,
        };
        apply();
    }, [apply]);

    const reset = useCallback(() => {
        view.current = { x: 0, y: 0, scale: 1 };
        apply();
    }, [apply]);

    useEffect(() => {
        let cancelled = false;
        fetch(withBase('/api/system_diagram.svg'))
            .then(async (res) => {
                const text = await res.text();
                if (!res.ok) {
                    let message = `${res.status} ${res.statusText || 'Request failed'}`;
                    try { message = JSON.parse(text).error || message; } catch (_) { /* not JSON */ }
                    throw new Error(message);
                }
                // Only the <svg> element is inlined; drop the XML prologue and
                // doctype. The markup is produced by Graphviz on our own
                // server, which escapes all text it embeds.
                const start = text.indexOf('<svg');
                if (start < 0) throw new Error('The server did not return an SVG document.');
                return text.slice(start);
            })
            .then((markup) => {
                if (cancelled) return;
                setSvg(markup);
                setError(null);
            })
            .catch((err) => {
                if (!cancelled) setError(err.message);
            })
            .finally(() => {
                if (!cancelled) setLoading(false);
            });
        return () => { cancelled = true; };
    }, []);

    // The legend is optional: if it cannot be loaded the diagram still shows.
    useEffect(() => {
        let cancelled = false;
        fetch(withBase('/api/system_diagram.json'))
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (!cancelled && data && Array.isArray(data.types)) setLegend(data);
            })
            .catch(() => { /* no legend */ });
        return () => { cancelled = true; };
    }, []);

    // Dim every component box whose fill is not the highlighted type's colour.
    useEffect(() => {
        const root = contentRef.current;
        if (!root) return;
        const wanted = highlight ? highlight.toLowerCase() : null;
        root.querySelectorAll('g.node').forEach((node) => {
            const title = node.querySelector('title');
            if (title && title.textContent.trim() === '__legend__') return;
            const shape = node.querySelector('polygon, path, ellipse');
            const fill = shape ? (shape.getAttribute('fill') || '').toLowerCase() : '';
            node.style.opacity = (!wanted || fill === wanted) ? '' : '0.12';
        });
    }, [highlight, svg]);

    // Fit the drawing once it is in the DOM.
    useEffect(() => {
        if (!svg) return undefined;
        const id = window.requestAnimationFrame(fit);
        return () => window.cancelAnimationFrame(id);
    }, [svg, fit]);

    // Wheel zoom needs a non-passive listener so the page does not scroll.
    useEffect(() => {
        const vp = viewportRef.current;
        if (!vp) return undefined;
        const onWheel = (e) => {
            e.preventDefault();
            const rect = vp.getBoundingClientRect();
            zoomBy(e.deltaY < 0 ? WHEEL_STEP : 1 / WHEEL_STEP,
                   e.clientX - rect.left, e.clientY - rect.top);
        };
        vp.addEventListener('wheel', onWheel, { passive: false });
        return () => vp.removeEventListener('wheel', onWheel);
    }, [zoomBy]);

    const onMouseDown = (e) => {
        if (e.button !== 0) return;
        moved.current = false;
        drag.current = {
            startX: e.clientX, startY: e.clientY,
            x: view.current.x, y: view.current.y,
        };
    };
    const onMouseMove = (e) => {
        const d = drag.current;
        if (!d) return;
        const dx = e.clientX - d.startX;
        const dy = e.clientY - d.startY;
        if (Math.abs(dx) + Math.abs(dy) > 3) moved.current = true;
        view.current.x = d.x + dx;
        view.current.y = d.y + dy;
        applyTransform();
    };
    const endDrag = () => { drag.current = null; };
    const onClick = (e) => {
        if (moved.current) {
            moved.current = false;   // that was a pan, not a click
            return;
        }
        const node = e.target.closest && e.target.closest('g.node');
        if (!node) return;
        const title = node.querySelector('title');
        const name = title && title.textContent ? title.textContent.trim() : '';
        if (name && !name.startsWith('__')) navigate(`/component/${encodeURIComponent(name)}`);
    };

    return (
        <Box sx={{ width: '96%', mx: 'auto', my: 2 }}>
            <Stack
                direction="row"
                alignItems="flex-start"
                justifyContent="space-between"
                flexWrap="wrap"
                sx={{ mb: 1, gap: 1 }}
            >
                <Box>
                    <Typography variant="h5" component="h1">System Diagram</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Boxes are components coloured by type, nesting shows
                        subcomponents, lines are current connections. Drag to
                        pan, scroll to zoom, click a component to open it.
                    </Typography>
                </Box>
                <Stack direction="row" spacing={1} alignItems="center">
                    <ButtonGroup size="small" variant="outlined" aria-label="zoom controls">
                        <Button onClick={() => zoomBy(1 / BUTTON_STEP)} aria-label="zoom out">&minus;</Button>
                        <Button onClick={() => zoomBy(BUTTON_STEP)} aria-label="zoom in">+</Button>
                        <Button onClick={fit}>Fit</Button>
                        <Button onClick={reset}>100%</Button>
                    </ButtonGroup>
                    <Typography
                        variant="body2"
                        data-testid="zoom-level"
                        sx={{ minWidth: 44, textAlign: 'right' }}
                    >
                        {scalePct}%
                    </Typography>
                    <Button
                        size="small"
                        component="a"
                        href={withBase('/api/system_diagram.svg')}
                        download="padloper-system.svg"
                    >
                        SVG
                    </Button>
                    <Button
                        size="small"
                        component="a"
                        href={withBase('/api/system_diagram.dot')}
                        download="padloper-system.dot"
                    >
                        DOT
                    </Button>
                </Stack>
            </Stack>

            <ErrorMessage errorMessage={error} />

            {legend && (
                <Stack direction="row" flexWrap="wrap" alignItems="center" sx={{ gap: 0.5, mb: 1 }} aria-label="legend">
                    {legend.types.map((t) => (
                        <Chip
                            key={t.name}
                            size="small"
                            label={`${t.name} (${t.count})`}
                            onClick={() => setHighlight((h) => (h === t.colour ? null : t.colour))}
                            sx={{
                                bgcolor: t.colour,
                                border: highlight === t.colour ? '2px solid #222' : '1px solid #bbb',
                                opacity: highlight && highlight !== t.colour ? 0.45 : 1,
                                '&:hover': { bgcolor: t.colour },
                            }}
                        />
                    ))}
                    {highlight && (
                        <Chip size="small" variant="outlined" label="Show all" onClick={() => setHighlight(null)} />
                    )}
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                        {legend.components} components, {legend.connections} connections.
                        Double border: contains subcomponents. Click a type to highlight it.
                    </Typography>
                </Stack>
            )}

            <Box
                ref={viewportRef}
                data-testid="diagram-viewport"
                onMouseDown={onMouseDown}
                onMouseMove={onMouseMove}
                onMouseUp={endDrag}
                onMouseLeave={endDrag}
                onClick={onClick}
                sx={{
                    position: 'relative',
                    height: 'calc(100vh - 210px)',
                    minHeight: 400,
                    overflow: 'hidden',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    bgcolor: '#fafafa',
                    cursor: 'grab',
                    userSelect: 'none',
                    '& svg': { display: 'block' },
                    '& g.node': { cursor: 'pointer' },
                    '& g.node:hover polygon, & g.node:hover path': { strokeWidth: 2.5 },
                }}
            >
                {loading && (
                    <CircularProgress sx={{ position: 'absolute', top: '45%', left: '48%' }} />
                )}
                {svg && (
                    <div
                        ref={contentRef}
                        data-testid="diagram-content"
                        style={{ transformOrigin: '0 0', position: 'absolute', left: 0, top: 0 }}
                        dangerouslySetInnerHTML={{ __html: svg }}
                    />
                )}
            </Box>
        </Box>
    );
}
