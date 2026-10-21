Shader "AssetLibrary/TransparentTwoSided"
{
    Properties
    {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Albedo (RGB) Alpha (A)", 2D) = "white" {}
        _BumpMap ("Normal Map", 2D) = "bump" {}
        _MetallicGlossMap ("Metallic (R) Smoothness (A)", 2D) = "white" {}
        _OcclusionMap ("Occlusion (G)", 2D) = "white" {}
        _OcclusionStrength ("Occlusion Strength", Range(0,1)) = 1
        _Metallic ("Metallic Multiplier", Range(0,1)) = 1
        _Glossiness ("Smoothness Multiplier", Range(0,1)) = 1
        _EmissionColor ("Emission", Color) = (0,0,0,0)
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull Mode", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "IgnoreProjector"="True" }
        Cull [_Cull]
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha
        LOD 300
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows alpha:fade keepalpha
        #pragma target 3.0
        sampler2D _MainTex;
        sampler2D _BumpMap;
        sampler2D _MetallicGlossMap;
        sampler2D _OcclusionMap;
        float4 _Color;
        float4 _EmissionColor;
        float _Metallic, _Glossiness, _OcclusionStrength;

        struct Input
        {
            float2 uv_MainTex;
            float2 uv_BumpMap;
            float2 uv_MetallicGlossMap;
            float2 uv_OcclusionMap;
            float facing : VFACE;
        };

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            fixed4 c = tex2D(_MainTex, IN.uv_MainTex) * _Color;
            o.Albedo = c.rgb;
            float3 n = UnpackNormal(tex2D(_BumpMap, IN.uv_BumpMap));
            n.xy = (IN.facing < 0.0) ? -n.xy : n.xy;
            o.Normal = n;
            half4 mg = tex2D(_MetallicGlossMap, IN.uv_MetallicGlossMap);
            o.Metallic = mg.r * _Metallic;
            o.Smoothness = mg.a * _Glossiness;
            o.Occlusion = lerp(1.0, tex2D(_OcclusionMap, IN.uv_OcclusionMap).g, _OcclusionStrength);
            o.Emission = _EmissionColor.rgb * c.rgb;
            o.Alpha = c.a;
        }
        ENDCG
    }
    FallBack "Transparent/Diffuse"
}
