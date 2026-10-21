using UnityEngine;

namespace AssetLibrary
{
    /// <summary>
    /// Lightweight orbit / pan / zoom camera used by the included Showcase scene.
    /// LMB drag = orbit, RMB drag = pan, wheel = zoom.
    /// </summary>
    public class OrbitCamera : MonoBehaviour
    {
        public Vector3 focus = new Vector3(0f, 3f, 4f);
        public float distance = 22f;
        public float yaw = -32f;
        public float pitch = 20f;
        public float orbitSpeed = 3.5f;
        public float panSpeed = 0.02f;
        public float zoomSpeed = 4f;
        public float minDistance = 2f;
        public float maxDistance = 90f;
        public bool autoRotate = false;
        public float autoRotateSpeed = 3f;

        private Vector3 _lastMouse;

        private void Start()
        {
            Apply();
        }

        private void Update()
        {
            if (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1))
                _lastMouse = Input.mousePosition;

            if (Input.GetMouseButton(0))
            {
                Vector3 delta = Input.mousePosition - _lastMouse;
                yaw += delta.x * orbitSpeed * 0.2f;
                pitch = Mathf.Clamp(pitch - delta.y * orbitSpeed * 0.2f, -85f, 85f);
                _lastMouse = Input.mousePosition;
            }
            else if (Input.GetMouseButton(1))
            {
                Vector3 delta = Input.mousePosition - _lastMouse;
                Vector3 right = transform.right;
                Vector3 up = transform.up;
                focus -= (right * delta.x + up * delta.y) * panSpeed * distance * 0.05f;
                _lastMouse = Input.mousePosition;
            }

            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.0001f)
                distance = Mathf.Clamp(distance * (1f - scroll * zoomSpeed * 0.1f), minDistance, maxDistance);

            if (autoRotate)
                yaw += autoRotateSpeed * Time.deltaTime;

            Apply();
        }

        private void Apply()
        {
            Quaternion rot = Quaternion.Euler(pitch, yaw, 0f);
            transform.position = focus + rot * new Vector3(0f, 0f, -distance);
            transform.rotation = rot;
        }
    }
}
