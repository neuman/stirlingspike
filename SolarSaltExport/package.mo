within ;
package SolarSaltExport
  "Closed-loop solar thermochemical heat export via salt hydration cycles"

  annotation(
    version = "0.1",
    versionDate = "2026-04-28",
    Documentation(info = "<html>
<p>Modelica package for end-to-end simulation of a solar thermochemical heat
export system. The cycle: hydrated salt is dehydrated in a solar charging
field at the source, shipped to a temperate destination, rehydrated to release
heat to a district heating network, then the discharged hydrated salt is
returned for re-charging.</p>

<p>Modules:</p>
<ul>
<li><b>Records</b> &mdash; chemistry property records (CaCl2, MgSO4, Mg(OH)2, Ca(OH)2)
and route property records.</li>
<li><b>Components</b> &mdash; SolarChargingField, HydrationReactor, BulkCarrier,
DistrictHeatPlant.</li>
<li><b>Examples</b> &mdash; full annual-cycle scenarios for the four candidate
geographic pairings.</li>
</ul>

<p>This package is the formal specification of the dynamic model. A faithful
Python mirror in <code>/sim</code> is used as the numerical runner for
parameter sweeps in environments where the OpenModelica compiler is
unavailable.</p>
</html>"));
end SolarSaltExport;
