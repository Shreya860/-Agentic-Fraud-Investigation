import { useApp } from "../context/AppContext";

export default function ToastStack() {
  const { toasts, dismissToast } = useApp();
  if (toasts.length === 0) return null;
  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast ${t.kind === "ok" ? "ok" : t.kind === "error" ? "error" : ""}`}
          role="status"
          onClick={() => dismissToast(t.id)}
          style={{ cursor: "pointer" }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}