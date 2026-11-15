// SPDX-License-Identifier: GPL-2.0-or-later
// Plasma's existing panel objects keep their position, height and other applets.
(function () {
    var replacements = {
        "org.kde.plasma.kickoff": "org.scarletprotocol.launcher",
        "org.kde.plasma.kicker": "org.scarletprotocol.launcher",
        "org.kde.plasma.digitalclock": "org.scarletprotocol.clock"
    };
    var result = [];
    var planned = [];
    var allPanels = panels();
    for (var p = 0; p < allPanels.length; p++) {
        var panel = allPanels[p];
        var existing = panel.widgets();
        for (var w = 0; w < existing.length; w++) {
            var original = existing[w];
            var destination = replacements[original.type];
            if (!destination) continue;
            original.currentConfigGroup = ["General"];
            var settings = {};
            var keys = original.configKeys;
            for (var k = 0; k < keys.length; k++) settings[keys[k]] = original.readConfig(keys[k]);
            var old = {panel: panel.id, type: original.type, index: original.index,
                       shortcut: original.globalShortcut, general: settings};
            planned.push({panel:panel,original:original,destination:destination,old:old});
        }
    }
    // Create every new applet before removing any existing applet.
    try {
        for (var i = 0; i < planned.length; i++) {
            var step = planned[i];
            step.replacement = step.panel.addWidget(step.destination);
            if (!step.replacement || step.replacement.type !== step.destination) {
                throw new Error("Could not load " + step.destination + ". The original applets were kept.");
            }
            step.replacement.currentConfigGroup = ["General"];
            if (step.destination === "org.scarletprotocol.launcher" && step.old.general.favoriteApps) {
                step.replacement.writeConfig("favoriteApps", step.old.general.favoriteApps);
            }
            var night = typeof scarletNightShift !== "undefined" && scarletNightShift;
            step.replacement.writeConfig("accentColor", night ? "#c93e62" : "#ff315b");
            step.replacement.writeConfig("glowStrength", night ? 45 : 70);
            step.replacement.reloadConfig();
        }
    } catch (error) {
        for (var j = 0; j < planned.length; j++) {
            if (planned[j].replacement) planned[j].replacement.remove();
        }
        throw error;
    }
    for (var i = 0; i < planned.length; i++) {
        var step = planned[i];
        step.replacement.index = step.old.index;
        step.original.globalShortcut = "";
        step.original.remove();
        if (step.old.shortcut) step.replacement.globalShortcut = step.old.shortcut;
        step.old.replacementId = step.replacement.id;
        result.push(step.old);
    }
    print(JSON.stringify({replaced: result.length, previous: result}));
})();
