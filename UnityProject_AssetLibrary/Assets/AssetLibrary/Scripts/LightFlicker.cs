using UnityEngine;

namespace AssetLibrary
{
    /// <summary>
    /// Optional candle / lamp flicker. Disabled by default on generated lamp prefabs -
    /// enable the component on the "Lamp Light" child to make the light pulse.
    /// </summary>
    [RequireComponent(typeof(Light))]
    public class LightFlicker : MonoBehaviour
    {
        public float minIntensity = 0.7f;
        public float maxIntensity = 1.25f;
        public float speed = 7f;

        private Light _light;
        private float _baseIntensity;
        private float _seed;

        private void Awake()
        {
            _light = GetComponent<Light>();
            _baseIntensity = _light.intensity;
            _seed = Random.value * 100f;
        }

        private void Update()
        {
            float n = Mathf.PerlinNoise(_seed, Time.time * speed) * 2f - 1f;
            float target = Mathf.Lerp(minIntensity, maxIntensity, (n + 1f) * 0.5f);
            _light.intensity = _baseIntensity * target;
        }
    }
}
