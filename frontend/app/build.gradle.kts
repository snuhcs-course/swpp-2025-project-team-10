import java.io.FileInputStream
import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.safeargs)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt)
    alias(libs.plugins.kover)
}

android {
    namespace = "com.example.librarytogether"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.librarytogether"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

//        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        testInstrumentationRunner = "com.example.librarytogether.CustomTestRunner"

        val localProps = Properties()
        val localFile = rootProject.file("local.properties")
        if (localFile.exists()) {
            localProps.load(FileInputStream(localFile))
        }

        buildConfigField("String", "KAKAO_API_KEY", "\"${localProps.getProperty("KAKAO_API_KEY", "")}\"")
        buildConfigField("String", "GOOGLE_API_KEY", "\"${localProps.getProperty("GOOGLE_API_KEY", "")}\"")
    }

    buildTypes {
        debug {
            enableAndroidTestCoverage = true
            enableUnitTestCoverage = false
        }

        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    testOptions {
        unitTests.isReturnDefaultValues = true
        unitTests.isIncludeAndroidResources = true
        unitTests.all {
            it.maxHeapSize = "2g"
            it.maxParallelForks = 1
            it.forkEvery = 100
            it.jvmArgs("-XX:+HeapDumpOnOutOfMemoryError")
        }
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            merges += "META-INF/LICENSE.md"
            merges += "META-INF/LICENSE-notice.md"
            merges += "META-INF/LICENSE"
            merges += "META-INF/NOTICE"
            merges += "META-INF/README"
        }
    }
}

dependencies {

    androidTestImplementation("androidx.test.espresso:espresso-intents:3.5.1")
    testImplementation("androidx.test.espresso:espresso-intents:3.5.1")
    testImplementation(libs.androidx.espresso.core)
    testImplementation(libs.androidx.espresso.contrib)
    testImplementation(libs.androidx.fragment.testing)
    testImplementation(libs.hilt.android.testing)
    kaptTest(libs.hilt.android.compiler)
    debugImplementation("com.google.dagger:hilt-android-testing:2.51.1")
    androidTestImplementation(libs.androidx.navigation.testing)
    implementation(libs.flowbinding.android)
    implementation(libs.androidx.hilt.navigation.fragment)
    testImplementation(libs.hamcrest)
    testImplementation(libs.truth)
    androidTestImplementation(libs.hilt.android.testing)
    kaptAndroidTest(libs.hilt.android.compiler)
    androidTestImplementation(libs.androidx.fragment.testing)
    androidTestImplementation(libs.androidx.test.runner)
    androidTestImplementation(libs.androidx.test.rules)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.espresso.contrib)
    androidTestImplementation(libs.mockito.android)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.mockito.core)
    testImplementation(libs.mockito.kotlin)
    testImplementation(libs.androidx.arch.core.testing)
    testImplementation(libs.junit)
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    implementation(libs.androidx.lifecycle.livedata.ktx)
    coreLibraryDesugaring(libs.android.desugarJdkLibs)
    kapt (libs.glide.compiler)
    kaptTest(libs.glide.compiler)
    implementation (libs.glide)
    implementation (libs.androidx.viewpager2)
    implementation(libs.retrofit)
    implementation(libs.gson)
    implementation(libs.retrofit.converter.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging.interceptor)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.activity)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.navigation.fragment.ktx)
    implementation(libs.androidx.navigation.ui.ktx)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    implementation(libs.google.auth)
    implementation("androidx.credentials:credentials:1.6.0-alpha05")
    implementation("androidx.credentials:credentials-play-services-auth:1.6.0-alpha05")
    implementation("com.google.android.libraries.identity.googleid:googleid:1.1.0")
    implementation("com.kakao.sdk:v2-user:2.20.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("de.hdodenhof:circleimageview:3.1.0")
    implementation("com.google.android.flexbox:flexbox:3.0.0")
    implementation("com.google.android.material:material:1.12.0")

    testImplementation("org.robolectric:robolectric:4.12.2")
}

kover {
    reports {
        // 'debug' 빌드 변형에 대한 리포트 설정
        variant("debug") {
            filters {
                excludes {
                    // 1. 안드로이드 시스템 관련 제외
                    classes(
                        "*.BuildConfig",
                        "*.R",
                        "*.R$*",
                        "*.Manifest",
                        "*.Manifest$*",
                        "android.*",
                        "androidx.*"
                    )

                    // 2. Hilt & Dagger 생성 파일 제외
                    // Kover는 와일드카드(*)를 사용하여 클래스 이름을 매칭합니다.
                    classes(
                        "*_MembersInjector",
                        "dagger.*",
                        "*_Factory",
                        "*_HiltModules*",
                        "hilt_aggregated_deps.*",
                        "*_Impl*", // Room이나 Retrofit 구현체 등
                        "*.di.*"   // di 패키지 내부
                    )

                    // 3. DataBinding/ViewBinding
                    classes(
                        "*databinding.*",
                        "*Binding"
                    )

                    // 4. 어노테이션 기반 제외 (유용함)
                    annotatedBy(
                        "dagger.internal.DaggerGenerated",
                        "javax.annotation.processing.Generated"
                    )
                }
            }

            // HTML 리포트 설정
            html {
                // 리포트가 생성될 경로 (기본값: build/reports/kover/html/debug)
                onCheck = true // ./gradlew check 실행 시 리포트 생성 여부
            }

            // XML 리포트 설정 (CI/CD 연동 시 필요)
            xml {
                onCheck = true
            }
        }
    }
}
