/**
 * Génère un plan de vol à partir des résultats des outils
 * Retourne la séquence de commandes qui seront envoyées au backend Python
 */

export interface FlightCommand {
  id: string;
  action: string;
  parameters: any;
  description: string;
}

export function generateFlightPlan(toolCalls: any[]): FlightCommand[] {
  const commands: FlightCommand[] = [];
  let commandId = 1;

  // Extraire les données des tool calls
  const allCoords = toolCalls.filter(tc => tc.name === 'getCoordonnees' && !tc.result.error);
  const etatInitial = toolCalls.find(tc => tc.name === 'getEtatInitial')?.result;
  const allMissionPlans = toolCalls.filter(tc => tc.name === 'planMissionRecon' && !tc.result.error);

  if (allCoords.length === 0 || !etatInitial) {
    return commands; // Pas assez de données
  }

  const cruiseAlt = etatInitial.cruise_alt || 50;
  const speed = etatInitial.speed || 5;
  const homeLat = etatInitial.home?.lat || 48.8566;
  const homeLon = etatInitial.home?.lon || 2.3522;

  // 1. Décollage (une seule fois au début)
  commands.push({
    id: `cmd_${commandId++}`,
    action: 'takeoff',
    parameters: { alt_m: cruiseAlt },
    description: `Décollage à ${cruiseAlt}m d'altitude`,
  });

  // Pour chaque site à inspecter
  for (let i = 0; i < allCoords.length; i++) {
    const coords = allCoords[i].result;
    const targetLat = coords.lat;
    const targetLon = coords.lon;
    const siteName = allCoords[i].arguments?.site_name || `Site ${i + 1}`;

    // Trouver le plan de mission correspondant (si disponible)
    const missionPlan = allMissionPlans.find(mp => {
      const mpArgs = mp.arguments;
      return Math.abs(mpArgs.lat - targetLat) < 0.001 && Math.abs(mpArgs.lon - targetLon) < 0.001;
    })?.result;

    // 2. Déplacement vers la cible
    commands.push({
      id: `cmd_${commandId++}`,
      action: 'goto',
      parameters: {
        lat: targetLat,
        lon: targetLon,
        alt_m: cruiseAlt,
        speed_mps: speed,
      },
      description: `Navigation vers ${siteName} (${targetLat.toFixed(4)}, ${targetLon.toFixed(4)}) à ${cruiseAlt}m`,
    });

    // 3. Orbite autour de la cible
    let radius = 200; // Par défaut
    if (missionPlan?.waypoints && missionPlan.waypoints.length > 0) {
      // Calculer le rayon à partir des waypoints
      const firstWaypoint = missionPlan.waypoints[0];
      const dLat = (firstWaypoint.lat - targetLat) * 111000; // mètres
      const dLon = (firstWaypoint.lon - targetLon) * 111000 * Math.cos(targetLat * Math.PI / 180);
      radius = Math.round(Math.sqrt(dLat * dLat + dLon * dLon));
    } else if (missionPlan?.radius_m) {
      radius = missionPlan.radius_m;
    }

    commands.push({
      id: `cmd_${commandId++}`,
      action: 'circle',
      parameters: {
        target_lat: targetLat,
        target_lon: targetLon,
        alt_m: cruiseAlt,
        radius_m: radius,
        laps: 1,
      },
      description: `Orbite autour de ${siteName} (rayon: ${radius}m)`,
    });

    // 4. Capture photo
    commands.push({
      id: `cmd_${commandId++}`,
      action: 'capture',
      parameters: {
        type: 'photo',
      },
      description: `Capture d'une photo de ${siteName}`,
    });
  }

  // 5. Retour au point de départ (une seule fois à la fin)
  commands.push({
    id: `cmd_${commandId++}`,
    action: 'rth',
    parameters: {},
    description: 'Retour au point de départ',
  });

  // 6. Atterrissage
  commands.push({
    id: `cmd_${commandId++}`,
    action: 'land',
    parameters: {},
    description: 'Atterrissage',
  });

  return commands;
}

