import { useId } from "react";

const SEGMENTS = [
  ["head", "neck"], ["neck", "shoulderL"], ["neck", "shoulderR"],
  ["shoulderL", "elbowL"], ["elbowL", "wristL"], ["shoulderR", "elbowR"], ["elbowR", "wristR"],
  ["neck", "hipCenter"], ["hipCenter", "hipL"], ["hipCenter", "hipR"],
  ["hipL", "kneeL"], ["kneeL", "ankleL"], ["hipR", "kneeR"], ["kneeR", "ankleR"],
];

const STANDING = {
  head: [160, 24], neck: [160, 46], shoulderL: [139, 56], shoulderR: [181, 56],
  elbowL: [130, 86], elbowR: [190, 86], wristL: [126, 116], wristR: [194, 116],
  hipCenter: [160, 102], hipL: [148, 106], hipR: [172, 106],
  kneeL: [147, 137], kneeR: [173, 137], ankleL: [145, 166], ankleR: [175, 166],
};
const pose = (changes) => ({ ...STANDING, ...changes });

const GRAPHS = {
  bodyweight_squat: { joints: pose({ hipCenter: [160, 112], hipL: [146, 116], hipR: [174, 116], kneeL: [127, 139], kneeR: [193, 139], ankleL: [143, 166], ankleR: [177, 166], elbowL: [126, 78], elbowR: [194, 78], wristL: [143, 86], wristR: [177, 86] }), ghost: STANDING, motion: "M218 82 C235 102 231 128 213 141" },
  sit_to_stand: { joints: STANDING, ghost: pose({ hipCenter: [160, 112], hipL: [148, 116], hipR: [172, 116], kneeL: [126, 139], kneeR: [194, 139], ankleL: [126, 166], ankleR: [194, 166] }), motion: "M220 137 C239 112 235 82 216 64", props: ["M112 118 H208 V126 H112 Z", "M119 126 V166", "M201 126 V166"] },
  knee_extension: { joints: pose({ hipCenter: [160, 103], hipL: [151, 108], hipR: [169, 108], kneeL: [131, 132], ankleL: [102, 133], kneeR: [190, 132], ankleR: [190, 163] }), ghost: pose({ hipCenter: [160, 103], hipL: [151, 108], hipR: [169, 108], kneeL: [131, 132], ankleL: [131, 163], kneeR: [190, 132], ankleR: [190, 163] }), motion: "M127 157 Q102 151 96 135", props: ["M137 109 H202 V118 H137 Z", "M194 118 V166"] },
  shoulder_abduction: { joints: pose({ elbowL: [105, 57], wristL: [72, 57], elbowR: [215, 57], wristR: [248, 57] }), ghost: STANDING, motion: "M111 104 Q84 88 75 63" },
  hip_abduction: { joints: pose({ kneeR: [202, 138], ankleR: [229, 153] }), ghost: STANDING, motion: "M184 158 Q211 166 230 154" },
  push_up: { joints: { head: [72, 66], neck: [91, 74], shoulderL: [100, 72], shoulderR: [100, 79], elbowL: [83, 104], elbowR: [91, 108], wristL: [61, 132], wristR: [69, 134], hipCenter: [167, 91], hipL: [158, 88], hipR: [165, 96], kneeL: [217, 105], kneeR: [221, 111], ankleL: [267, 122], ankleR: [271, 128] }, ghost: { head: [72, 46], neck: [94, 55], shoulderL: [104, 54], shoulderR: [104, 61], elbowL: [104, 90], elbowR: [112, 94], wristL: [61, 132], wristR: [69, 134], hipCenter: [171, 74], hipL: [162, 71], hipR: [169, 79], kneeL: [220, 91], kneeR: [224, 97], ankleL: [267, 122], ankleR: [271, 128] }, motion: "M49 66 Q39 91 53 116", props: ["M38 139 H284"] },
  shoulder_press: { joints: pose({ elbowL: [128, 57], wristL: [132, 25], elbowR: [192, 57], wristR: [188, 25] }), ghost: pose({ elbowL: [132, 81], wristL: [132, 57], elbowR: [188, 81], wristR: [188, 57] }), motion: "M111 72 Q105 45 125 27" },
  bicep_curl: { joints: pose({ elbowL: [130, 87], wristL: [143, 61], elbowR: [190, 87], wristR: [177, 61] }), ghost: STANDING, motion: "M111 112 Q102 80 137 61" },
  hammer_curl: { joints: pose({ elbowL: [130, 87], wristL: [137, 58], elbowR: [190, 87], wristR: [183, 58] }), ghost: STANDING, motion: "M210 111 Q219 79 188 58", props: ["M132 51 V63", "M188 51 V63"] },
  heel_raise: { joints: pose({ ankleL: [147, 159], ankleR: [173, 159] }), ghost: STANDING, motion: "M205 164 V139", props: ["M137 166 L153 161", "M167 161 L183 166"] },
  lunge: { joints: pose({ hipCenter: [160, 105], hipL: [149, 110], hipR: [171, 110], kneeL: [116, 137], ankleL: [82, 164], kneeR: [192, 137], ankleR: [225, 164] }), ghost: STANDING, motion: "M218 95 Q240 121 226 157" },
  step_up: { joints: pose({ hipCenter: [160, 97], hipL: [149, 102], hipR: [171, 102], kneeL: [132, 129], ankleL: [113, 146], kneeR: [184, 127], ankleR: [184, 164] }), ghost: STANDING, motion: "M102 158 Q92 137 110 119", props: ["M73 148 H151 V166 H73", "M151 166 H224"] },
  balance: { joints: pose({ kneeR: [188, 133], ankleR: [164, 142], elbowL: [111, 74], wristL: [87, 81], elbowR: [209, 74], wristR: [233, 81] }), ghost: STANDING, motion: "M218 150 Q231 132 220 113" },
  walking_gait_screen: { joints: pose({ shoulderL: [143, 57], shoulderR: [179, 54], elbowL: [157, 82], wristL: [177, 102], elbowR: [164, 81], wristR: [145, 104], hipL: [150, 106], hipR: [170, 103], kneeL: [129, 136], ankleL: [104, 164], kneeR: [192, 132], ankleR: [219, 158] }), ghost: STANDING, motion: "M81 151 H53", props: ["M69 169 H248"] },
  shoulder_flexion: { joints: pose({ elbowL: [139, 40], wristL: [145, 15], elbowR: [181, 40], wristR: [175, 15] }), ghost: STANDING, motion: "M112 102 Q101 48 137 19" },
  hip_flexion: { joints: pose({ kneeR: [195, 112], ankleR: [196, 143] }), ghost: STANDING, motion: "M206 151 Q222 125 199 108" },
};

function Skeleton({ joints, ghost = false }) {
  return (
    <g opacity={ghost ? 0.28 : 1} stroke={ghost ? "#94a3b8" : "currentColor"} strokeWidth={ghost ? 4 : 5} strokeLinecap="round" strokeLinejoin="round">
      {SEGMENTS.map(([from, to]) => joints[from] && joints[to] ? <line key={`${from}-${to}`} x1={joints[from][0]} y1={joints[from][1]} x2={joints[to][0]} y2={joints[to][1]} /> : null)}
      {Object.entries(joints).map(([name, [x, y]]) => name === "head"
        ? <circle key={name} cx={x} cy={y} r={ghost ? 9 : 10} fill={ghost ? "#f8fafc" : "white"} />
        : <circle key={name} cx={x} cy={y} r={ghost ? 2.5 : 3.5} fill="white" />)}
    </g>
  );
}

export default function ExercisePoseGraph({ exerciseId, label, supported = true }) {
  const markerId = `motion-${useId().replaceAll(":", "")}`;
  const graph = GRAPHS[exerciseId] || { joints: STANDING };
  return (
    <svg viewBox="0 0 320 180" role="img" aria-label={label} data-exercise-pose={exerciseId} className={`h-full w-full ${supported ? "text-clinical-blue" : "text-slate-500"}`}>
      <title>{label}</title>
      <defs><marker id={markerId} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#0f9f95" /></marker></defs>
      <ellipse cx="160" cy="169" rx="113" ry="5" fill={supported ? "#dbeafe" : "#e2e8f0"} opacity="0.75" />
      {graph.props?.map((path) => <path key={path} d={path} fill="none" stroke="#64748b" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />)}
      {graph.ghost ? <Skeleton joints={graph.ghost} ghost /> : null}
      <Skeleton joints={graph.joints} />
      {graph.motion ? <path d={graph.motion} fill="none" stroke="#0f9f95" strokeWidth="4" strokeLinecap="round" strokeDasharray="6 6" markerEnd={`url(#${markerId})`} /> : null}
    </svg>
  );
}

export { GRAPHS as EXERCISE_POSE_GRAPHS };
