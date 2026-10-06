using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace StorybookCast.Editor
{
    public static class StorybookShoulderReview
    {
        [Serializable] public class Check { public bool ok; public string key; public int frames, caps, points; public float maxMappingError, maxTorsoLocalDrift; }
        class Anchor { public Transform bone; public int[] indices; public Vector3[] local; }
        static Vector3[] Vertices(SkinnedMeshRenderer skin, Mesh scratch)
        { skin.BakeMesh(scratch); var points=scratch.vertices; for(int i=0;i<points.Length;i++) points[i]=skin.transform.TransformPoint(points[i]); return points; }
        public static string VerifyCharacter(string key, string directory)
        {
            var spec=StorybookAssets.ReadCatalog().characters.Single(c=>c.key==key);
            if(spec.shoulders==null || spec.shoulders.Length!=2) throw new Exception("Missing shoulder metadata: "+key);
            var scene=EditorSceneManager.NewPreviewScene(); var scratch=new Mesh();
            var report=new Check {key=key,caps=2};
            try
            {
                var actor=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(StorybookAssets.ThemeRoot(spec.theme)+"/Prefabs/"+key+".prefab"),scene);
                var skin=actor.GetComponentInChildren<SkinnedMeshRenderer>(); var clips=StorybookAssets.Clips(spec); clips.Single(c=>c.name=="Idle").SampleAnimation(actor,0);
                var rest=Vertices(skin,scratch);var anchors=new List<Anchor>();
                foreach(var shoulder in spec.shoulders)
                {
                    var body=skin.bones.Single(b=>b.name==shoulder.body_bone);int count=shoulder.root_points.Length/3;
                    var ids=new int[count];var local=new Vector3[count];
                    for(int i=0;i<count;i++)
                    {
                        // Blender front -Y becomes Unity -Z; FBX import includes unit/axis conversion.
                        var expected=new Vector3(shoulder.root_points[i*3],shoulder.root_points[i*3+2],shoulder.root_points[i*3+1]);
                        int closest=-1;float distance=float.PositiveInfinity;
                        for(int v=0;v<rest.Length;v++) {float d=(rest[v]-expected).sqrMagnitude;if(d<distance){distance=d;closest=v;}}
                        float error=Mathf.Sqrt(distance);report.maxMappingError=Mathf.Max(report.maxMappingError,error);
                        if(error>.001f) throw new Exception(key+" "+shoulder.side+": imported cap mapping error "+error);
                        ids[i]=closest;local[i]=body.InverseTransformPoint(rest[closest]);
                    }
                    anchors.Add(new Anchor{bone=body,indices=ids,local=local});report.points+=count;
                }
                foreach(var clip in clips)
                {
                    int last=Mathf.RoundToInt(clip.length*24);
                    for(int frame=0;frame<=last;frame++)
                    {
                        clip.SampleAnimation(actor,Mathf.Min((float)frame/24,clip.length));var points=Vertices(skin,scratch);
                        foreach(var anchor in anchors) for(int i=0;i<anchor.indices.Length;i++)
                        {
                            float drift=Vector3.Distance(anchor.bone.InverseTransformPoint(points[anchor.indices[i]]),anchor.local[i]);
                            report.maxTorsoLocalDrift=Mathf.Max(report.maxTorsoLocalDrift,drift);
                            if(drift>.0005f) throw new Exception(key+"/"+clip.name+"/"+frame+": shoulder separates from torso "+drift);
                        }
                        report.frames++;
                    }
                }
                if(report.frames!=368)throw new Exception("Unexpected frame count "+report.frames);report.ok=true;
            }
            finally {UnityEngine.Object.DestroyImmediate(scratch);EditorSceneManager.ClosePreviewScene(scene);}
            Directory.CreateDirectory(directory);string json=JsonUtility.ToJson(report,true);File.WriteAllText(Path.Combine(directory,key+"-shoulder-unity.json"),json);return json;
        }
    }
}
