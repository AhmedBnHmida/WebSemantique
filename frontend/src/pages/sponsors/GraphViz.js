import React, { useMemo } from 'react';
import './GraphViz.css';

// Lightweight SVG-based graph renderer (no external libs).
// Sponsors on left column, Donations on right column; straight links between them.
const GraphViz = ({ sponsors = [], donations = [], graphData = null, width = 900, height = 600 }) => {
  // Build nodes and links. If graphData is provided, use authoritative nodes/edges from backend.
  const { nodesList, links } = useMemo(() => {
    if (graphData && graphData.nodes) {
      // Normalize nodes: ensure id, label, types, properties
      const nodes = graphData.nodes.map(n => ({
        id: n.id,
        label: n.label || (n.id && (n.id.split('#').pop() || n.id.split('/').pop())),
        types: n.types || [],
        properties: n.properties || {}
      }));
      const edges = (graphData.edges || []).map(e => ({ source: e.source, target: e.target, predicate: e.predicate }));
      return { nodesList: nodes, links: edges };
    }

    // Fallback: use simple heuristic-based layout from sponsors/donations
    // Map sponsor display name -> sponsor object
    const sponsorMap = sponsors.map((s, i) => {
      const name = s.nomEntreprise || s.companyName || s.firstName || s.name || s.label || 'Sponsor ' + i;
      return { id: `s_${i}`, label: name, types: ['Sponsor'], raw: s };
    });

    // Donation nodes
    const donationMap = donations.map((d, i) => {
      const label = d.rdfs_label || d.donation || d.label || d.rdfsLabel || d.name || `Donation ${i}`;
      return { id: `d_${i}`, label, types: ['Donation'], raw: d };
    });

    // Helper to find sponsor index from donation raw fields (several possible shapes)
    const findSponsorIndex = (donation) => {
      const donorCandidates = [
        donation.donateur,
        donation.donorName,
        donation.donor,
        donation.madeBy,
        donation.sponsor,
        donation.sponsorName,
        donation.creator
      ].filter(Boolean).map(String);

      if (donorCandidates.length === 0) return -1;

      for (let i = 0; i < sponsorMap.length; i++) {
        const sname = sponsorMap[i].label;
        if (donorCandidates.includes(sname)) return i;
        // also try contains
        for (const cand of donorCandidates) {
          if (sname && cand && (sname.includes(cand) || cand.includes(sname))) return i;
        }
      }
      return -1;
    };

    const linkList = [];
    donationMap.forEach((dn, di) => {
      const donation = dn.raw;
      const sponsorIdx = findSponsorIndex(donation);
      if (sponsorIdx >= 0) {
        linkList.push({ source: sponsorMap[sponsorIdx].id, target: dn.id });
      } else {
        // try to infer from sponsor URI fields on sponsors (makesDonation links)
        for (let si = 0; si < sponsorMap.length; si++) {
          const sraw = sponsorMap[si].raw;
          if (!sraw) continue;
          const makes = sraw.makesDonation || sraw.makesDonations || sraw.makesDonationId || sraw.donations;
          if (!makes) continue;
          const cand = Array.isArray(makes) ? makes : [makes];
          for (const c of cand) {
            if (!c) continue;
            const cStr = String(c);
            if (cStr.includes(dn.label) || cStr.includes(dn.id) || cStr.includes(dn.label.replace(/\s/g, ''))) {
              linkList.push({ source: sponsorMap[si].id, target: dn.id });
            }
          }
        }
      }
    });

    return { nodesList: [...sponsorMap, ...donationMap], links: linkList };
  }, [sponsors, donations, graphData]);

  // layout: vertical spacing
  const padding = 40;

  // Layout nodes into columns by type when graphData provided, otherwise left/right simple layout
  const typeColumns = {
    Sponsor: 0,
    Donation: 1,
    Event: 2,
  };

  // assign a column index based on node types; default to 1
  // Filter nodes/edges to only include Sponsor/Donation/Event when graphData provided
  let filteredNodes = nodesList;
  let filteredLinks = links;
  if (graphData && graphData.nodes) {
    // Accept any type that ends with Sponsor/Donation/Event (captures subclasses like FinancialDonation)
    const keepType = (t) => {
      if (!t) return false;
      const short = String(t).split('#').pop().split('/').pop();
      const s = short.toLowerCase();
      return s.endsWith('sponsor') || s.endsWith('donation') || s.endsWith('event');
    };
    // keep nodes that have at least one matching type
    filteredNodes = nodesList.filter(n => (n.types || []).some(keepType));
    const allowedIds = new Set(filteredNodes.map(n => n.id));
    filteredLinks = links.filter(l => allowedIds.has(l.source) && allowedIds.has(l.target));
  }

  const nodesWithPos = filteredNodes.map((n, idx) => {
    // determine primary type
    let col = 1;
    if (n.types && n.types.length > 0) {
      const t = n.types[0].split('#').pop().split('/').pop();
      if (typeColumns.hasOwnProperty(t)) col = typeColumns[t];
    }
    return { ...n, col, idx };
  });

  // columns count
  const cols = Math.max(...nodesWithPos.map(n => n.col)) + 1;
  const colWidth = (width - padding * 2) / Math.max(cols, 1);

  // group nodes by column to compute vertical positions
  const groups = {};
  nodesWithPos.forEach(n => { groups[n.col] = groups[n.col] || []; groups[n.col].push(n); });

  const positioned = [];
  Object.keys(groups).forEach(colKey => {
    const col = parseInt(colKey, 10);
    const group = groups[col];
    const count = group.length || 1;
    group.forEach((n, i) => {
      const x = padding + col * colWidth + 20;
      const y = padding + (i + 0.5) * ((height - padding * 2) / count);
      positioned.push({ ...n, x, y });
    });
  });

  const nodesById = {};
  positioned.forEach(n => nodesById[n.id] = n);

  return (
    <div className="graphviz-container" style={{ width: '100%', overflow: 'auto' }}>
      <svg width={Math.min(width, 1100)} height={height} className="graphviz-svg">
        {/* draw links */}
        <g className="links">
          {filteredLinks.map((l, i) => {
            const s = nodesById[l.source];
            const t = nodesById[l.target];
            if (!s || !t) return null;
            // compute centers (rect x = n.x - 10, width = 160 => center = n.x + 70)
            const x1 = s.x + 70;
            const y1 = s.y;
            const x2 = t.x + 70;
            const y2 = t.y;
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2;
            const predicateLabel = l.predicateLabel || (l.predicate ? l.predicate.split('#').pop().split('/').pop() : 'rel');
            const labelWidth = Math.max(48, predicateLabel.length * 7);
            const labelHeight = 18;
            return (
              <g key={i} className="edge-group">
                <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#777" strokeWidth={1.5} />
                {/* background rect for label */}
                <rect className="edge-label-rect" x={midX - labelWidth / 2} y={midY - labelHeight / 2} width={labelWidth} height={labelHeight} rx={4} ry={4} fill="#fff" stroke="#ddd" />
                <text className="edge-label-text" x={midX} y={midY + 5} textAnchor="middle" fontSize={11} fill="#333">{predicateLabel}</text>
              </g>
            );
          })}
        </g>

        {/* sponsors */}
        {/* nodes */}
        <g className="nodes">
          {positioned.map((n) => {
            const isSponsor = n.types && n.types.some(t => t.toLowerCase().endsWith('sponsor'));
            const isDonation = n.types && n.types.some(t => t.toLowerCase().endsWith('donation'));
            const fill = isSponsor ? '#2b8cbe' : (isDonation ? '#66c2a5' : '#f7a35c');
            const textColor = isSponsor ? '#fff' : '#033';
            return (
              <g key={n.id} className={`node ${isSponsor ? 'sponsor-node' : (isDonation ? 'donation-node' : 'other-node')}`}>
                <rect x={n.x - 10} y={n.y - 14} width={160} height={28} rx={6} ry={6} fill={fill} />
                <text x={n.x + 8} y={n.y + 5} fill={textColor} fontSize={11}>{n.label}</text>
              </g>
            )
          })}
        </g>
      </svg>

      {links.length === 0 && (
        <div className="graph-empty">Aucune relation détectée — vérifiez que vos donations ont un champ "donor"/"donateur" ou que sponsors contiennent `makesDonation` URIs.</div>
      )}

      {/* legend */}
      <div className="graph-legend">
        <div className="legend-item"><span className="legend-swatch sponsor"/> Sponsor</div>
        <div className="legend-item"><span className="legend-swatch donation"/> Donation</div>
        <div className="legend-item"><span className="legend-swatch event"/> Event</div>
      </div>
    </div>
  );
};

export default GraphViz;
