import { useState } from "react";
import Card from "../components/Card";
import { useApp } from "../context/AppContext";

export default function Settings() {
  const { pushToast } = useApp();

  const [profile, setProfile] = useState({ name: "A. Kapoor", email: "a.kapoor@example.com", role: "Senior Fraud Analyst" });
  const [notify, setNotify] = useState({ email: true, slack: false, sms: false, highRiskOnly: true });
  const [prefs, setPrefs] = useState({ autoCreate: true, autoAssign: false, showGraphOnOpen: true });
  const [thresholds, setThresholds] = useState({ low: 30, moderate: 55, high: 80 });
  const [ui, setUi] = useState({ density: "comfortable", theme: "light" });

  const save = (section: string) => pushToast(`${section} settings saved locally (mock).`, "ok");

  return (
    <div className="stack">
      <Card title="Profile">
        <div className="grid grid-2">
          <label>
            <div className="section-title">Name</div>
            <input className="input" style={{ width: "100%" }} value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
          </label>
          <label>
            <div className="section-title">Email</div>
            <input className="input" style={{ width: "100%" }} value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
          </label>
          <label>
            <div className="section-title">Role</div>
            <input className="input" style={{ width: "100%" }} value={profile.role} onChange={(e) => setProfile({ ...profile, role: e.target.value })} />
          </label>
        </div>
        <div className="mt-3">
          <button className="btn btn-primary" onClick={() => save("Profile")}>Save</button>
        </div>
      </Card>

      <Card title="Notification Preferences">
        <div className="stack" style={{ gap: 8 }}>
          <Toggle label="Email notifications"    checked={notify.email}        onChange={(v) => setNotify({ ...notify, email: v })} />
          <Toggle label="Slack notifications"    checked={notify.slack}        onChange={(v) => setNotify({ ...notify, slack: v })} />
          <Toggle label="SMS alerts"             checked={notify.sms}          onChange={(v) => setNotify({ ...notify, sms: v })} />
          <Toggle label="Only alert on high risk" checked={notify.highRiskOnly} onChange={(v) => setNotify({ ...notify, highRiskOnly: v })} />
        </div>
        <div className="mt-3"><button className="btn btn-primary" onClick={() => save("Notification")}>Save</button></div>
      </Card>

      <Card title="Investigation Preferences">
        <div className="stack" style={{ gap: 8 }}>
          <Toggle label="Auto-create investigation for very high risk" checked={prefs.autoCreate}       onChange={(v) => setPrefs({ ...prefs, autoCreate: v })} />
          <Toggle label="Auto-assign to least-loaded analyst"          checked={prefs.autoAssign}       onChange={(v) => setPrefs({ ...prefs, autoAssign: v })} />
          <Toggle label="Open graph by default on case view"           checked={prefs.showGraphOnOpen} onChange={(v) => setPrefs({ ...prefs, showGraphOnOpen: v })} />
        </div>
        <div className="mt-3"><button className="btn btn-primary" onClick={() => save("Investigation")}>Save</button></div>
      </Card>

      <Card title="Risk Thresholds">
        <div className="grid grid-3">
          <label>
            <div className="section-title">Low → Moderate</div>
            <input className="input" type="number" style={{ width: "100%" }} value={thresholds.low} onChange={(e) => setThresholds({ ...thresholds, low: Number(e.target.value) })} />
          </label>
          <label>
            <div className="section-title">Moderate → High</div>
            <input className="input" type="number" style={{ width: "100%" }} value={thresholds.moderate} onChange={(e) => setThresholds({ ...thresholds, moderate: Number(e.target.value) })} />
          </label>
          <label>
            <div className="section-title">High → Very High</div>
            <input className="input" type="number" style={{ width: "100%" }} value={thresholds.high} onChange={(e) => setThresholds({ ...thresholds, high: Number(e.target.value) })} />
          </label>
        </div>
        <div className="mt-3"><button className="btn btn-primary" onClick={() => save("Risk threshold")}>Save</button></div>
      </Card>

      <Card title="UI Preferences">
        <div className="grid grid-2">
          <label>
            <div className="section-title">Density</div>
            <select className="select" style={{ width: "100%" }} value={ui.density} onChange={(e) => setUi({ ...ui, density: e.target.value })}>
              <option value="comfortable">Comfortable</option>
              <option value="compact">Compact</option>
            </select>
          </label>
          <label>
            <div className="section-title">Theme</div>
            <select className="select" style={{ width: "100%" }} value={ui.theme} onChange={(e) => setUi({ ...ui, theme: e.target.value })}>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </label>
        </div>
        <div className="mt-3"><button className="btn btn-primary" onClick={() => save("UI")}>Save</button></div>
      </Card>

      <Card title="System Information">
        <dl className="kv">
          <dt>Frontend Version</dt><dd className="mono">0.1.0 (hackathon)</dd>
          <dt>Data Mode</dt><dd><span className="badge badge-neutral">Mock (backend-independent)</span></dd>
          <dt>Backend</dt><dd>Not connected — replace <span className="mono">dataService.ts</span> later.</dd>
          <dt>Graph</dt><dd>Mock graph data (SVG)</dd>
        </dl>
      </Card>
    </div>
  );
}

function Toggle({
  label, checked, onChange,
}: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="row" style={{ gap: 8, cursor: "pointer" }}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="small">{label}</span>
    </label>
  );
}